from husky.asynctasks.tasks import spider_task

print spider_task.delay(1).get()