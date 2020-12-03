from socket import *
import json
import io
import struct
from translate import Translator
from pymongo import MongoClient
import re, math
from collections import Counter
import difflib
import sys

mdbClient = MongoClient("mongodb+srv://Test:Test@cluster0.v7zkv.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = mdbClient.get_database("Office_Bearer_Info")
record = db.Employee_Records


class Message:
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
		return json.dumps(obj).encode('utf-8')

	def json_decode(self,json_bytes):
		return json.loads(json_bytes.decode('utf-8')) 

	def compute_checksum(self,message):
		checksum=0
		l=len(message)
		if(l%2==1):
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
									# print(int(checksum))
									# print(hex(checksum))
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
						if('number' in self.headers and self.headers['number']=='1'):
							self.recv_data=self.recv_data[checksum_length:]
							self.answers={'first':self.answers}
							header_length = 2
							msg=b""
							if(len(self.recv_data)>=header_length):
								msg=msg+self.recv_data[:header_length]
								self.headers_length=struct.unpack(">H",self.recv_data[:header_length])[0]
								self.recv_data=self.recv_data[header_length:]

							if(True):
								headers_length=self.headers_length
								if(len(self.recv_data)>=headers_length):
									self.headers=self.json_decode(self.recv_data[:headers_length])
									msg=msg+self.recv_data[:headers_length]
									self.recv_data=self.recv_data[headers_length:]

							content_length=self.headers["content_length"]
							checksum_length=2
							if(True):
								answers=self.recv_data[:content_length]
								msg=msg+self.recv_data[:content_length]
								self.recv_data=self.recv_data[content_length:]
								answers=self.json_decode(answers)
								c1=self.compute_checksum(msg)
								checksum=int.from_bytes(self.recv_data[:checksum_length], "big") 
								c2=self.verify(msg,checksum)
								if(c2==0xFFFF):
									self.recv_data=b""
									self.answers['second']=answers
									self.process_response()
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
		if number == 2 or number == 3:
			# print("Server checksum")
			# print(hex(d))
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
		if(lang!='English'):
			translator= Translator(to_lang=lang)
		if(auth=='0'):
			find=list(record.find({'name':name}))
			if(len(find)>0):
				find=find[0]
				result=0
				if('all' in find['auth']):
					if(lang!='English'):
						result=translator.translate('Not authorised')
					else:
						result='Not authorised'
					content={'name':name,'gen':result}
					message=self.create_message(content,'0',auth,lang)
					self.send_data=message
					self.write_server()
				else:
					find=list(record.find({'name':name}))
					if(len(find)>0):
						find=find[0]
						content={'name':name}
						translation=0
						for i in questions:
							if(i not in find['auth'] and i!='name'):
								if(lang!='English'):
									translation = translator.translate(find[i])
								else:
									translation=find[i]
								content[i]=translation
							elif(i!='name'):
								if(lang!='English'):
									translation = translator.translate('Not authorised')
								else:
									translation='Not authorised'
								content[i]=translation
						message=self.create_message(content,'0',auth,lang)
						self.send_data=message
						self.write_server()
			else:
				if(True):
					possible=[]
					message_1=0
					message_2=0
					find=list(record.find({}))
					for i in find:
						possible.append(i['name'])
					m=difflib.get_close_matches(name,possible,len(possible),0)
					if(True):
						find=list(record.find({'name':m[0]}))
						if(len(find)>0):
							find=find[0]
							content={'name':find['name']}
							result=0
							if('all' in find['auth']):
								if(lang!='English'):
									result=translator.translate('Not authorised')
								else:
									result='Not authorised'
								content={'name':find['name'],'gen':result}
								message_1=self.create_message(content,'0',auth,lang,2)

							else:
								translation=0
								for i in questions:
									if(i not in find['auth'] and i!='name'):
										if(lang!='English'):
											translation = translator.translate(find[i])
										else:
											translation=find[i]
										content[i]=translation
									elif(i!='name'):
										if(lang!='English'):
											translation = translator.translate('Not authorised')
										else:
											translation='Not authorised'
										content[i]=translation

								message_1=self.create_message(content,'0',auth,lang,2)
						find=list(record.find({'name':m[1]}))
						if(len(find)>0):
							find=find[0]
							result=0
							content={'name':find['name']}
							if('all' in find['auth']):
								if(lang!='English'):
									result=translator.translate('Not authorised')
								else:
									result='Not authorised'
								content={'gen':result,'name':find['name']}
								message_2=self.create_message(content,'0',auth,lang,3)

							else:
								translation=0
								for i in questions:
									if(i not in find['auth'] and i!='name'):
										if(lang!='English'):
											translation = translator.translate(find[i])
										else:
											translation=find[i]
										content[i]=translation
									elif(i!='name'):
										if(lang!='English'):
											translation = translator.translate('Not authorised')
										else:
											translation='Not authorised'
										content[i]=translation
								message_2=self.create_message(content,'0',auth,lang,3)
						self.send_data=message_1+message_2
						self.write_server()


		else:
			find=list(record.find({'name':name}))
			if(len(find)>0):
				find=find[0]
				translation=0
				content={'name':name}
				for i in questions:
					if(i!='name'):
						if(lang!='English'):
							translation = translator.translate(find[i])
						else:
							translation=find[i]
						content[i]=translation
				message=self.create_message(content,'0',auth,lang)
				self.send_data=message
				self.write_server()
			else:
				possible=[]
				find=list(record.find({}))
				for i in find:
					possible.append(i['name'])
				m=difflib.get_close_matches(name,possible,len(possible),0)
				if(True):
					find=list(record.find({'name':m[0]}))
					translation=0
					if(len(find)>0):
						find=find[0]
						content={'name':find['name']}
						for i in questions:
							if(i!='name'):
								if(lang!='English'):
									translation = translator.translate(find[i])
								else:
									translation=find[i]
								content[i]=translation
						message_1=self.create_message(content,'0',auth,lang,2)
						find=list(record.find({'name':m[1]}))
						if(len(find)>0):
							find=find[0]
							content={'name':find['name']}
							translation=0
							for i in questions:
								if(i!='name'):
									if(lang!='English'):
										translation = translator.translate(find[i])
									else:
										translation=find[i]
									content[i]=translation
						message_2=self.create_message(content,'0',auth,lang,3)
						self.send_data=message_1+message_2
						self.write_server()