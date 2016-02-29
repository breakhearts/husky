from experiments.retry import add

print add.delay(1,2).get()