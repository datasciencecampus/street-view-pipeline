from pystalkd.Beanstalkd import Connection

beanstalk = Connection(host='localhost', port=11300)
print("tubes:", beanstalk.tubes())
print("switching to", beanstalk.watch('manchester'))
print("now watching", beanstalk.watching())

while True:
    print("blocking...")
    job = beanstalk.reserve()
    print("got job:", job.body)
    job.delete()   

