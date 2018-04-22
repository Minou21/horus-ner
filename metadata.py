import urllib
import urllib2

class Web4MexCreator:
	token = ''
	resultPath = ''
	
	def __init__(self, path="SampleWeb4MexFile.txt"):
		self.token = self.getToken()
		#self.token = '05635b00-31ab-488b-ad97-3838637f3e8a'
		self.resultPath = path
	
	def getToken(self):
		request = urllib2.Request('http://52.173.249.140:3011/token')
		response = urllib2.urlopen(request)
		return response.read()
	
	def setAuthorName(self, author):
		headers = {"Accept" : "*/*"}
		request = urllib2.Request('https://52.173.249.140:3011/%s/authorEmail?%s' %(self.token, author))
		request.add_header("Accept", "*/*")
		response = urllib2.urlopen(request)
		if response.code != 200:
			return False
		else: 
			return True
		
	def getResult(self):
		url = 'http://52.173.249.140:3011/%s/serialize?format=ttl' % (self.token)
		request = urllib2.Request(url)
		response = urllib2.urlopen(request)
		if response.code != 200:
			return False
		else:
			content = response.read();
			file = open(self.resultPath, "w")
			file.write(content)
			file.close
			return True
	
if __name__ == '__main__':
	creator = Web4MexCreator()
	print creator.token
	#creator.setAuthorName("testname")
	if not creator.getResult():
		print "no valid response from Web4Mex. File could not be created"
	
	