import json
from socket import *
import io
import sys
import struct
from translate import Translator
from pymongo import MongoClient

mdbClient = MongoClient("mongodb+srv://Test:Test@cluster0.v7zkv.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = mdbClient.get_database("Office_Bearer_Info")
record = db.Employee_Records


class protocol:
	def __init__(self,sock,server,port):
		self.sock=sock
		self.recv_data=b""
		self.send_data=b""
		self.headers_length=None
		self.headers=None
		self.questions=None
		self.answers=None
		self.client=None
		self.server=server
		self.port=port


	def json_encode(self,obj):
		#return json.dumps(obj, ensure_ascii=False).encode("utf-8")
		return json.dumps(obj).encode('utf-8')

	def json_decode(self,json_bytes):
		'''tiow = io.TextIOWrapper(io.BytesIO(json_bytes), encoding="utf-8", newline="")
		obj = json.load(tiow)
		tiow.close()
		return obj'''
		return json.loads(json_bytes.decode('utf-8')) 

	def compute_checksum(self,message):
		checksum=0
		l=len(message)
		if(l%2==1):
			#message=message+struct.pack("!B", 0)
			l=l+1
			xs = bytearray(message)
			xs.append(0)
			message =bytes(xs)

		for i in range(0, l, 2):
			checksum=checksum+(message[i] << 8)+(message[i+1])

		checksum = (checksum >> 16) + (checksum & 0xFFFF)
		checksum = ~checksum & 0xFFFF
		return checksum

	def verify(self,message,checksum):
		message=bytes(message)
		l=len(message)
		if(l%2==1):
			l=l+1
			xs = bytearray(message)
			xs.append(0)
			message =bytes(xs)
		for i in range(0, l, 2):
			checksum=checksum+(message[i] << 8)+(message[i + 1])
		checksum=(checksum >> 16)+(checksum & 0xFFFF)
		return checksum


	def write_client(self,content,authentication,lang):

		message=self.create_message(content,'1',authentication,lang)
		self.sock.sendto(message,(self.server, self.port))

	def read_server(self):
		try:
			recv_data,addr=self.sock.recvfrom(4096)
			self.client=addr
		except Exception:
			pass
		else:
			if(recv_data):
				self.recv_data=self.recv_data+recv_data
				msg=b""
				if(self.headers_length is None):
					header_length = 2
					if(len(self.recv_data)>=header_length):
						msg=msg+self.recv_data[:header_length]
						self.headers_length=struct.unpack(">H",self.recv_data[:header_length])[0]
						self.recv_data=self.recv_data[header_length:]

						if(self.headers is None):
							headers_length=self.headers_length
							if(len(self.recv_data)>=headers_length):
								self.headers=self.json_decode(self.recv_data[:headers_length])
								msg=msg+self.recv_data[:headers_length]
								self.recv_data=self.recv_data[headers_length:]

								content_length=self.headers["content_length"]
								checksum_length=2
								if(len(self.recv_data)>=content_length):
									questions=self.recv_data[:content_length]
									msg=msg+self.recv_data[:content_length]
									self.recv_data=self.recv_data[content_length:]
									self.questions=self.json_decode(questions)
									
									c1=self.compute_checksum(msg)
									checksum=int.from_bytes(self.recv_data[:checksum_length], "big") 
									c=self.verify(msg,checksum)
									if(c==0xFFFF):
										self.recv_data=b""
										self.process_request()

	def process_response(self):
		print(json.dumps(self.answers))


	def read_client(self):
		try:
			recv_data,addr=self.sock.recvfrom(4096)
		except Exception:
			pass
		else:
			if(recv_data):
				self.recv_data=self.recv_data+recv_data
				msg=b""
				if(self.headers_length is None):
					header_length = 2
					if(len(self.recv_data)>=header_length):
						msg=msg+self.recv_data[:header_length]
						self.headers_length=struct.unpack(">H",self.recv_data[:header_length])[0]
						self.recv_data=self.recv_data[header_length:]

				if(self.headers is None):
					headers_length=self.headers_length
					if(len(self.recv_data)>=headers_length):
						self.headers=self.json_decode(self.recv_data[:headers_length])
						msg=msg+self.recv_data[:headers_length]
						self.recv_data=self.recv_data[headers_length:]

				content_length=self.headers["content_length"]
				checksum_length=2
				if(len(self.recv_data)>=content_length):
					answers=self.recv_data[:content_length]
					msg=msg+self.recv_data[:content_length]
					self.recv_data=self.recv_data[content_length:]
					self.answers=self.json_decode(answers)
					c1=self.compute_checksum(msg)
					checksum=int.from_bytes(self.recv_data[:checksum_length], "big") 
					c=self.verify(msg,checksum)
					if(c==0xFFFF):
						if('number' in self.headers and self.headers['number']==1):
							self.recv_data=self.recv_data[checksum_length:]
							# Do work for second response
						else:
							self.recv_data=b""
							self.process_response()


	def create_message(self,content,request,authentication,lang,number=1):
		headers={'request':request,'lang':lang}
		content=self.json_encode(content)
		headers['content_length']=len(content)
		headers['authentication']=authentication
		if(number!=1):
			headers['number']=str(number-1)
		header_bytes = self.json_encode(headers)
		message_hdr = struct.pack(">H", len(header_bytes))
		msg = message_hdr + header_bytes + content
		d=self.compute_checksum(msg)
		c= d.to_bytes(2, 'big')
		message=msg+c
		return message


	def write_server(self):
		if(self.send_data):
			try:
				self.sock.sendto(self.send_data,self.client)
			except Exception:
				pass

			

	def process_request(self):
		name=self.questions['name']
		auth=self.headers['authentication']
		lang=self.headers['lang']
		questions=self.questions
		translator= Translator(to_lang=lang)
		if(auth=='0'):
			find=record.find_one({"name" : name})
			if('all' in find['auth']):
				result=translator.translate('Not authorised')
				content={'gen':result}
				message=self.create_message(content,'0',auth,lang)
				self.send_data=message
				self.write_server()
			else:
				find=list(record.find({'name':name}))
				if(len(find)>0):
					find=find[0]
					content={'name':name}
					for i in questions:
						if(i not in find['auth']):
							translation = translator.translate(find[i])
							content[i]=translation
						else:
							translation = translator.translate('Not authorised')
							content[i]=translation
					message=self.create_message(content,'0',auth,lang)
					self.send_data=message
					self.write_server()
				else:
					pass
