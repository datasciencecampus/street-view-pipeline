#!/bin/bash
## localhost
## note: -b persistent option.
beanstalkd -l 127.0.0.1 -p 11300 -b store/ &
