from django.db import models


class User(models.Model):
    email = models.CharField(max_length=50, primary_key=True)
    username = models.CharField(max_length=20, unique=True, null=False)
    password = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.username


class Session(models.Model):
    key = models.CharField(max_length=36, primary_key=True)
    data = models.CharField(max_length=200)


class Professor(models.Model):
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=20, null=False)

    def __str__(self):
        return self.id + '-' + self.name


class Module(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50, null=False)

    def __str__(self):
        return self.code + '-' + self.name


class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    professors = models.ManyToManyField(Professor)
    semester = models.CharField(max_length=5)
    year = models.CharField(max_length=5)

    class Meta:
        unique_together = ('module', 'semester', 'year')

    def __str__(self):
        return self.module.code + '-'+ self.module.name + \
               '-' + self.year + '-' + self.semester


class RatingRecord(models.Model):
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    rating = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.professor.name + '-' + str(self.rating)



