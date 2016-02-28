from experiments.test_retry import add

print add.delay(1,2).get()