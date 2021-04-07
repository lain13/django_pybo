"""
pybo models
"""
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db import models


class Question(models.Model):
    """
    질문모델
    """
    owning_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='question_owning_user')
    owning_group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE, related_name='question_owning_group')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    voter = models.ManyToManyField(User, related_name='question_voter')
    # auto_now_add를 적용해서 작성시에만 현재 날짜가 삽입되도록한다.
    createdon = models.DateTimeField(auto_now_add=True)
    # auto_now를 적용해서 작성시/갱신시 현재 날짜가 삽입되도록한다.
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_createdby')
    modifiedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_modifiedby')

    @property
    def owner(self):
        """
        owning user or group
        """
        if hasattr(self, 'owning_user'):
            return self.owning_user
        if hasattr(self, 'owning_group'):
            return self.owning_group
        return None

    @owner.setter
    def owner(self, owner):
        """
        소유자를 설정합니다.
        """
        if isinstance(owner, User):
            self.owning_user = owner
            self.owning_group = None
        elif isinstance(owner, Group):
            self.owning_user = None
            self.owning_group = owner
        else:
            raise Exception("소유자는 유저 또는 그룹을 설정할수 있습니다.")

    def __str__(self):
        return self.subject


class Answer(models.Model):
    """
    답변모델
    """
    owning_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='answer_owning_user')
    owning_group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE, related_name='answer_owning_group')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    voter = models.ManyToManyField(User, related_name='answer_voter')
    # auto_now_add를 적용해서 작성시에만 현재 날짜가 삽입되도록한다.
    createdon = models.DateTimeField(auto_now_add=True)
    # auto_now를 적용해서 작성시/갱신시 현재 날짜가 삽입되도록한다.
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_createdby')
    modifiedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_modifiedby')

    @property
    def owner(self):
        """
        owning user or group
        """
        if hasattr(self, 'owning_user'):
            return self.owning_user
        if hasattr(self, 'owning_group'):
            return self.owning_group
        return None

    @owner.setter
    def owner(self, owner):
        """
        소유자를 설정합니다.
        """
        if isinstance(owner, User):
            self.owning_user = owner
            self.owning_group = None
        elif isinstance(owner, Group):
            self.owning_user = None
            self.owning_group = owner
        else:
            raise Exception("소유자는 유저 또는 그룹을 설정할수 있습니다.")


class Comment(models.Model):
    """
    댓글모델
    """
    owning_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='comment_owning_user')
    owning_group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE, related_name='comment_owning_group')
    content = models.TextField()
    voter = models.ManyToManyField(User, related_name='comment_voter')
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)
    # auto_now_add를 적용해서 작성시에만 현재 날짜가 삽입되도록한다.
    createdon = models.DateTimeField(auto_now_add=True)
    # auto_now를 적용해서 작성시/갱신시 현재 날짜가 삽입되도록한다.
    modifiedon = models.DateTimeField(auto_now=True)
    createdby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_createdby')
    modifiedby = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_modifiedby')

    @property
    def owner(self):
        """
        owning user or group
        """
        if hasattr(self, 'owning_user'):
            return self.owning_user
        if hasattr(self, 'owning_group'):
            return self.owning_group
        return None

    @owner.setter
    def owner(self, owner):
        """
        소유자를 설정합니다.
        """
        if isinstance(owner, User):
            self.owning_user = owner
            self.owning_group = None
        elif isinstance(owner, Group):
            self.owning_user = None
            self.owning_group = owner
        else:
            raise Exception("소유자는 유저 또는 그룹을 설정할수 있습니다.")
