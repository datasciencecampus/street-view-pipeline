from pystalkd.Beanstalkd import Connection

beanstalk = Connection(host='localhost', port=11300)
print("tubes:", beanstalk.tubes())
print("switching to", beanstalk.use('manchester'))
print("now using", beanstalk.using())

print("sending job...")
beanstalk.put("meh")

