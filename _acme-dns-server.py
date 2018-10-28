#!/usr/bin/python

from twisted.internet import reactor, defer
from twisted.names import dns, error, server
from twisted.web import http

#config 
txt_content = 'this is a TXT Record test!'
password    = 'passwd'
http_port   = 80

class DynamicResolver(object):
	"""
	A resolver which calculates the answers to certain queries based on the
	query type and name.
	"""

	def _doDynamicResponse(self, query):
		"""
		Calculate the response to a query.
		"""
		print ('name' , query.name.name)

		payload = dns.Record_TXT( txt_content , ttl = 5)

		answer  = dns.RRHeader(
			name=query.name.name ,
			payload=payload,
			type=dns.TXT,
			ttl = 5 ,
		)

		answers    = [answer]
		authority  = []
		additional = []
		return answers, authority, additional


	def query(self, query, timeout=None):
		"""
		Check if the query should be answered dynamically, otherwise dispatch to
		the fallback resolver.
		"""
		if query.type == dns.TXT:
			return defer.succeed(self._doDynamicResponse(query))
		else:
			return defer.fail(error.DomainError())



class MyRequestHandler(http.Request):
	resources={
		'/':"<h1>Home</h1>This is TXT Record Tool for Let's Encrypt!<p> /set-txt?key=????????&txt=********<p><p> current :<p>",
		}
	def process(self):
		global txt_content , password
		self.setHeader('Content-Type','text/html')
		if self.path == '/':
			self.write( "%s%s" % (self.resources[self.path] , txt_content) )
		elif self.path == '/set-txt':
			key = self.args.get('key')
			txt = self.args.get('txt')
			print(key,txt)
			if key[0] == password and txt:
				txt_content = txt[0]
				self.write('Set ok!')
			else:
				self.write('Set error!')
		else:
			self.setResponseCode(http.NOT_FOUND)
			self.write("<h1>Not Found</h1>Sorry, no such source")
		self.finish()

class MyHTTP(http.HTTPChannel):
	requestFactory=MyRequestHandler

class MyHTTPFactory(http.HTTPFactory):
	def buildProtocol(self,addr):
		return MyHTTP()


def main():

	factory = server.DNSServerFactory( clients=[DynamicResolver()])
	protocol = dns.DNSDatagramProtocol(controller=factory)
	reactor.listenUDP(53, protocol)


	reactor.listenTCP(http_port,MyHTTPFactory())

	reactor.run()


if __name__ == '__main__':
	raise SystemExit(main())
