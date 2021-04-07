import logging

from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404
from django.shortcuts import resolve_url
from django.shortcuts import redirect
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Count

from django.views.generic import TemplateView
from django.views import View
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import HttpRequest

from django.db.models.query import QuerySet

from .models import Question
from .models import Answer
from .models import Comment
from .forms import QuestionForm
from .forms import AnswerForm
from .forms import CommentForm

logger = logging.getLogger('pybo')


class QuestionCreateView(LoginRequiredMixin, CreateView):
    """
    pybo 질문등록 클래스 뷰
    """
    form_class: type = QuestionForm
    # template_name기본값 'pybo/question_form.html'
    template_name: str = 'pybo/question_form.html'

    def form_valid(self, form: AnswerForm)->HttpResponseRedirect:
        """
        form.instance에 작성하려고하는 객체가 들어 있다.
        여기에 추가로 필요한 항목을 채워 넣는다.
        질문폼 클래스가 모델폼이기 때문에 객체의 저장은 부모 클래스에서 처리해준다.
        """
        form.instance.owner = self.request.user
        form.instance.createdby = self.request.user
        form.instance.modifiedby = self.request.user
        return super().form_valid(form)

    def get_success_url(self)->str:
        """
        보존에 성공했을때 리다이렉트되는 url
        """
        messages.info(self.request, '질문을 등록했습니다.')
        logger.info('redirect URL:{0}', resolve_url('pybo:index'))
        return resolve_url('pybo:index')


class QuestionModifyView(LoginRequiredMixin, UpdateView):
    """
    pybo 질문수정 클래스 뷰
    """
    model: type = Question
    form_class: type = QuestionForm
    # template_name기본값 'pybo/question_form.html'
    template_name: str = "pybo/question_form.html"

    def get_object(self, *args, **kwargs)->Answer:
        """
        get_object 메서드에서 객체에 대한 권한을 체크한다.
        """
        obj = super().get_object(*args, **kwargs)
        if obj.owner != self.request.user:
            raise PermissionDenied('댓글수정권한이 없습니다.')
        return obj

    def form_valid(self, form: QuestionForm)->HttpResponseRedirect:
        """
        form.instance에 작성하려고하는 객체가 들어 있다.
        여기에 추가로 필요한 항목을 채워 넣는다.
        객체의 저장은 부모 클래스에서 처리한다.
        """
        form.instance.owner = self.request.user
        form.instance.modifiedby = self.request.user
        return super().form_valid(form)

    def get_queryset(self)->QuerySet:
        """
        관련 데이터를 한번에 불러들이기위해서 get_queryset메서드를 오버라이드 한다.
        """
        return super().get_queryset().select_related('owning_user', 'owning_group')

    def get_success_url(self)->str:
        """
        수정에 성공했을때 리다이렉트되는 url
        """
        question = self.object
        messages.info(self.request, '질문댓글을 수정했습니다.')
        logger.info('redirect URL:{0}', resolve_url('pybo:detail', pk=question.id))
        return resolve_url('pybo:detail', pk=question.id)


class QuestionDeleteView(LoginRequiredMixin, DeleteView):
    """
    pybo 질문삭제
    get메서드의 확인화면을 스킵하고 싶으면
    delete메서드를 직접 호출한다.
    """
    model: type = Question
    # template_name기본값 'pybo/question_confirm_delete.html'

    def get_object(self, *args, **kwargs)->Question:
        """
        get_object 메서드에서 객체에 대한 권한을 체크한다.
        """
        obj = super().get_object(*args, **kwargs)
        if obj.owner != self.request.user:
            raise PermissionDenied('질문 삭제권한이 없습니다.')
        return obj

    def get_success_url(self)->str:
        """
        삭제에 성공했을때 리다이렉트되는 url
        """
        messages.info(self.request, '질문을 삭제했습니다.')
        logger.info('redirect URL:{0}', resolve_url('pybo:index'))
        return resolve_url('pybo:index')

class AnswerCreateView(LoginRequiredMixin, CreateView):
    """
    pybo 답변등록 클래스 뷰
    """
    form_class: type = AnswerForm
    template_name: str = 'pybo/question_detail.html'

    def form_valid(self, form: AnswerForm)->HttpResponseRedirect:
        """
        폼 검증이 처리된경우
        form.instance에 작성하려고하는 객체가 들어 있다.
        여기에 추가로 필요한 항목을 채워 넣는다.
        객체의 저장은 부모 클래스에서 처리한다.
        success_url주소로 리다이렉트한다.
        """
        logger.info('AnswerCreateView form_valid')
        form.instance.owner = self.request.user  # 추가한 속성 owner 적용
        form.instance.createdby = self.request.user
        form.instance.modifiedby = self.request.user
        form.instance.question = Question(pk=self.kwargs['question_id'])
        return super().form_valid(form)

    def form_invalid(self, form: AnswerForm)->HttpResponse:
        """
        폼 검증이 처리되지 않은경우
        그후에 template_name으로 렌더링된다.
        여기에서는 상세화면에서 답변을 등록하기 때문에 상세화면을 렌더링하기 위해
        필요한 질문 레코드를 취득해서 컨텍스트에 설정한다.
        """
        logger.info('AnswerCreateView form_invalid')
        context = self.get_context_data()
        context['form'] = form
        context['question'] = get_object_or_404(Question, pk=self.kwargs['question_id'])
        return self.render_to_response(context)

    def get_success_url(self)->str:
        """
        보존에 성공했을때 리다이렉트되는 url
        """
        logger.info('AnswerCreateView get_success_url')
        # self.object에 저장된 객체가 들어 있으니 다시 취득할 필요는 없다.
        answer = self.object
        messages.info(self.request, '답변을 등록했습니다.')
        logger.info('redirect URL:{0}#answer_{1}',
            resolve_url('pybo:detail', pk=answer.question.id), answer.id)
        return '{0}#answer_{1}'.format(
            resolve_url('pybo:detail', pk=answer.question.id), answer.id)

class AnswerModifyView(LoginRequiredMixin, UpdateView):
    """
    pybo 답변수정
    """
    model: type = Answer
    form_class: type = AnswerForm
    template_name: str = "pybo/answer_form.html"

    def get_object(self, *args, **kwargs)->Answer:
        """
        get_object 메서드에서 객체에 대한 권한을 체크한다.
        """
        logger.info('AnswerModifyView get_object')
        obj = super().get_object(*args, **kwargs)
        if obj.owner != self.request.user:
            raise PermissionDenied('수정권한이 없습니다.')
        return obj

    def form_valid(self, form: AnswerForm)->HttpResponseRedirect:
        """
        form.instance에 작성하려고하는 객체가 들어 있다.
        여기에 추가로 필요한 항목을 채워 넣는다.
        객체의 저장은 부모 클래스에서 처리한다.
        """
        logger.info('AnswerModifyView form_valid')
        form.instance.owner = self.request.user
        form.instance.modifiedby = self.request.user
        return super().form_valid(form)

    def get_queryset(self)->QuerySet:
        """
        관련 데이터를 한번에 불러들이기위해서 get_queryset메서드를 오버라이드 한다.
        """
        logger.info('AnswerModifyView get_queryset')
        return super().get_queryset().select_related('question')

    def get_success_url(self)->str:
        """
        수정에 성공했을때 리다이렉트되는 url
        """
        logger.info('AnswerModifyView get_success_url')
        answer = self.object
        messages.info(self.request, '답변을 수정했습니다.')
        logger.info('redirect URL:{}#answer_{}',
            resolve_url('pybo:detail', pk=answer.question.id), answer.id)
        return '{}#answer_{}'.format(
            resolve_url('pybo:detail', pk=answer.question.id), answer.id)

class AnswerDeleteView(LoginRequiredMixin, DeleteView):
    """
    pybo 답변삭제
    """
    model: type = Answer
    # default template_name 'pybo/answer_confirm_delete.html'

    def get_object(self, *args, **kwargs)->Answer:
        """
        get_object 메서드에서 객체에 대한 권한을 체크한다.
        """
        logger.info('AnswerDeleteView get_object')
        obj = super().get_object(*args, **kwargs)
        if obj.owner != self.request.user:
            raise PermissionDenied('삭제권한이 없습니다.')
        return obj

    def get_success_url(self)->str:
        """
        삭제에 성공했을때 리다이렉트되는 url
        """
        logger.info('AnswerDeleteView get_success_url')
        answer = self.object
        messages.info(self.request, '답변을 삭제했습니다.')
        logger.info(resolve_url('pybo:detail', pk=answer.question.id))
        return resolve_url('pybo:detail', pk=answer.question.id)

class IndexView(TemplateView):
    """
    pybo 목록 출력
    """

    template_name: str = 'pybo/question_list.html'

    def get(self, request: HttpRequest, *args, **kwargs)->HttpResponse:
        """
        pybo 목록 출력
        """
        logger.info("pybo 목록을 출력합니다.")
        # 입력 파라미터
        page = request.GET.get('page', '1')  # 페이지
        kw = request.GET.get('kw', '')  # 검색어
        so = request.GET.get('so', 'recent')  # 정렬기준

        # 정렬
        if so == 'recommend':
            question_list = Question.objects.annotate(num_voter=Count('voter')).order_by('-num_voter', '-createdon')
        elif so == 'popular':
            question_list = Question.objects.annotate(num_answer=Count('answer')).order_by('-num_answer', '-createdon')
        else:  # recent
            question_list = Question.objects.order_by('-createdon')

        # 검색
        if kw:
            question_list = question_list.filter(
                Q(subject__icontains=kw) |  # 제목검색
                Q(content__icontains=kw) |  # 내용검색
                Q(createdby__username__icontains=kw) |  # 질문 글쓴이검색
                Q(answer__createdby__username__icontains=kw)  # 답변 글쓴이검색
            ).distinct()

        # 페이징처리
        paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
        page_obj = paginator.get_page(page)

        context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so}  # <------ so 추가
        return self.render_to_response(context)

class QuestionDetailView(DetailView):
    """
    pybo 내용 출력
    """
    model: type = Question
    template_name: str = 'pybo/question_detail.html'

    def get_queryset(self)->QuerySet:
        """
        관련 데이터를 한번에 불러들이기위해서 get_queryset메서드를 오버라이드 한다.
        """
        logger.info('QuestionDetailView get_queryset')
        return super().get_queryset().select_related('createdby', 'modifiedby')


class CommentCreateQuestionView(LoginRequiredMixin, CreateView):
    """
    pybo 질문댓글등록 클래스 뷰
    """
    form_class: type = CommentForm
    # template_name기본값 'pybo/question_form.html'
    template_name: str = 'pybo/comment_form.html'

    def form_valid(self, form: CommentForm)->HttpResponseRedirect:
        """
        form.instance에 작성하려고하는 객체가 들어 있다.
        여기에 추가로 필요한 항목을 채워 넣는다.
        객체의 저장은 부모 클래스에서 처리한다.
        """
        logger.info('CommentCreateQuestionView form_valid')
        form.instance.owner = self.request.user
        form.instance.createdby = self.request.user
        form.instance.modifiedby = self.request.user
        form.instance.question = Question(pk=self.kwargs['question_id'])
        return super().form_valid(form)

    def get_success_url(self)->str:
        """
        보존에 성공했을때 리다이렉트되는 url
        """
        logger.info('CommentCreateQuestionView get_success_url')
        comment = self.object
        messages.info(self.request, '답변을 등록했습니다.')
        logger.info('redirect URL:{}#comment_{}'.format(
            resolve_url('pybo:detail', pk=comment.question.id), comment.id))
        return '{}#comment_{}'.format(
            resolve_url('pybo:detail', pk=comment.question.id), comment.id)


class CommentModifyQuestionView(LoginRequiredMixin, UpdateView):
    """
    pybo 질문댓글수정 클래스 뷰
    """
    model: type = Comment
    form_class: type = CommentForm
    template_name: str = "pybo/comment_form.html"

    def get_object(self, *args, **kwargs)->Answer:
        """
        get_object 메서드에서 객체에 대한 권한을 체크한다.
        """
        logger.info('CommentModifyQuestionView get_object')
        obj = super().get_object(*args, **kwargs)
        if obj.owner != self.request.user:
            raise PermissionDenied('수정권한이 없습니다.')
        return obj

    def form_valid(self, form: AnswerForm)->HttpResponseRedirect:
        """
        form.instance에 작성하려고하는 객체가 들어 있다.
        여기에 추가로 필요한 항목을 채워 넣는다.
        객체의 저장은 부모 클래스에서 처리한다.
        """
        logger.info('CommentModifyQuestionView form_valid')
        form.instance.owner = self.request.user
        form.instance.modifiedby = self.request.user
        return super().form_valid(form)

    def get_queryset(self)->QuerySet:
        """
        관련 데이터를 한번에 불러들이기위해서 get_queryset메서드를 오버라이드 한다.
        """
        logger.info('CommentModifyQuestionView get_queryset')
        return super().get_queryset().select_related('question', 'createdby', 'modifiedby')

    def get_success_url(self)->str:
        """
        수정에 성공했을때 리다이렉트되는 url
        """
        logger.info('CommentModifyQuestionView get_success_url')
        comment = self.object
        messages.info(self.request, '질문댓글을 수정했습니다.')
        logger.info('redirect URL:{}#comment_{}',
            resolve_url('pybo:detail', pk=comment.question.id), comment.id)
        return '{}#comment_{}'.format(
            resolve_url('pybo:detail', pk=comment.question.id), comment.id)


class CommentDeleteQuestionView(LoginRequiredMixin, DeleteView):
    """
    pybo 질문댓글삭제
    """
    model: type = Comment
    # template_name기본값 'pybo/comment_confirm_delete.html'

    def get_object(self, *args, **kwargs)->Answer:
        """
        get_object 메서드에서 객체에 대한 권한을 체크한다.
        """
        logger.info('CommentDeleteQuestionView get_object')
        obj = super().get_object(*args, **kwargs)
        if obj.owner != self.request.user:
            raise PermissionDenied('댓글 삭제권한이 없습니다.')
        return obj

    def get_success_url(self)->str:
        """
        삭제에 성공했을때 리다이렉트되는 url
        """
        logger.info('CommentDeleteQuestionView get_success_url')
        comment = self.object
        messages.info(self.request, '댓글을 삭제했습니다.')
        logger.info(resolve_url('pybo:detail', pk=comment.question.id))
        return resolve_url('pybo:detail', pk=comment.question.id)


class CommentCreateAnswerView(LoginRequiredMixin, CreateView):
    """
    pybo 답글댓글등록 클래스 뷰
    """
    form_class: type = CommentForm
    # template_name기본값 'pybo/comment_form.html'
    template_name: str = 'pybo/comment_form.html'

    def form_valid(self, form: CommentForm)->HttpResponseRedirect:
        """
        form.instance에 작성하려고하는 객체가 들어 있다.
        여기에 추가로 필요한 항목을 채워 넣는다.
        객체의 저장은 부모 클래스에서 처리한다.
        """
        logger.info('CommentCreateAnswerView form_valid')
        form.instance.owner = self.request.user
        form.instance.createdby = self.request.user
        form.instance.modifiedby = self.request.user
        form.instance.answer = get_object_or_404(Answer, pk=self.kwargs['answer_id'])
        return super().form_valid(form)

    def get_success_url(self)->str:
        """
        보존에 성공했을때 리다이렉트되는 url
        """
        logger.info('CommentCreateAnswerView get_success_url')
        comment = self.object
        #answer = get_object_or_404(Answer, pk=comment.answer.id)
        messages.info(self.request, '답변을 등록했습니다.')
        logger.info('redirect URL:{}#comment_{}'.format(
            resolve_url('pybo:detail', pk=comment.answer.question.id), comment.id))
        return '{}#comment_{}'.format(
            resolve_url('pybo:detail', pk=comment.answer.question.id), comment.id)


class CommentModifyAnswerView(LoginRequiredMixin, UpdateView):
    """
    pybo 답글댓글수정 클래스 뷰
    """
    model = Comment
    form_class = CommentForm
    template_name: str = "pybo/comment_form.html"

    def get_object(self, *args, **kwargs)->Answer:
        """
        get_object 메서드에서 객체에 대한 권한을 체크한다.
        """
        logger.info('CommentModifyAnswerView get_object')
        obj = super().get_object(*args, **kwargs)
        if obj.owner != self.request.user:
            raise PermissionDenied('댓글수정권한이 없습니다.')
        return obj

    def form_valid(self, form: AnswerForm)->HttpResponseRedirect:
        """
        form.instance에 작성하려고하는 객체가 들어 있다.
        여기에 추가로 필요한 항목을 채워 넣는다.
        객체의 저장은 부모 클래스에서 처리한다.
        """
        logger.info('CommentModifyAnswerView form_valid')
        form.instance.owner = self.request.user
        form.instance.modifiedon = timezone.now()
        form.instance.modifiedby = self.request.user
        return super().form_valid(form)

    def get_queryset(self)->QuerySet:
        """
        관련 데이터를 한번에 불러들이기위해서 get_queryset메서드를 오버라이드 한다.
        """
        logger.info('CommentModifyAnswerView get_queryset')
        return super().get_queryset().select_related('answer', 'createdby', 'modifiedby')

    def get_success_url(self)->str:
        """
        수정에 성공했을때 리다이렉트되는 url
        """
        logger.info('CommentModifyAnswerView get_success_url')
        comment = self.object
        messages.info(self.request, '질문댓글을 수정했습니다.')
        logger.info('redirect URL:{}#comment_{}',
            resolve_url('pybo:detail', pk=comment.answer.question.id), comment.id)
        return '{}#comment_{}'.format(
            resolve_url('pybo:detail', pk=comment.answer.question.id), comment.id)


class CommentDeleteAnswerView(LoginRequiredMixin, DeleteView):
    """
    pybo 답글댓글삭제
    """
    model: type = Comment
    # default template_name 'pybo/comment_confirm_delete.html'

    def get_object(self, *args, **kwargs)->Comment:
        """
        get_object 메서드에서 객체에 대한 권한을 체크한다.
        """
        logger.info('CommentDeleteAnswerView get_object')
        obj = super().get_object(*args, **kwargs)
        if obj.owner != self.request.user:
            raise PermissionDenied('답글 댓글 삭제권한이 없습니다.')
        return obj

    def get_success_url(self)->str:
        """
        삭제에 성공했을때 리다이렉트되는 url
        """
        logger.info('CommentDeleteAnswerView get_success_url')
        comment = self.object
        messages.info(self.request, '답글 댓글을 삭제했습니다.')
        logger.info(resolve_url('pybo:detail', pk=comment.answer.question.id))
        return resolve_url('pybo:detail', pk=comment.answer.question.id)

class VoteQuestionView(LoginRequiredMixin, View):
    """
    pybo 질문추천등록
    """

    def get(self, request: HttpRequest, *args, **kwargs)->HttpResponseRedirect:
        """
        pybo 질문추천등록
        """
        question = get_object_or_404(Question, pk=kwargs['question_id'])
        if request.user == question.owner:
            messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
        else:
            question.voter.add(request.user)
        return redirect('pybo:detail', pk=question.id)

class VoteAnswerView(LoginRequiredMixin, View):
    """
    pybo 답글추천등록
    """

    def get(self, request: HttpRequest, *args, **kwargs)->HttpResponseRedirect:
        """
        pybo 답글추천등록
        """
        answer = get_object_or_404(Answer, pk=kwargs['answer_id'])
        if request.user == answer.owner:
            messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
        else:
            answer.voter.add(request.user)
        return redirect('pybo:detail', pk=answer.question.id)
