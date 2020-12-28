from django.urls import path

from .views import BbIndexView, ByRubricListView, BbCreateView, BbDetailView, leave_comment, \
    BbEditView, BbDeleteView, ClientRoom, RegisterUserView, BboardLoginView, BboardLogoutView, \
    RubricCreateView, RubricDeleteView, rubrics, process_search_results, ImgCreateView

app_name = 'bboard'

urlpatterns = [
    path('rubric/<int:rubric_id>/', ByRubricListView.as_view(), name='by_rubric'),
    path('', BbIndexView.as_view(), name='index'),
    path('add/', BbCreateView.as_view(), name='add'),
    path('add/rubric', RubricCreateView.as_view(), name='add_rubric'),
    path('add/rubric/formset/', rubrics, name='add_rubric_formset'),
    path('add/file/', ImgCreateView.as_view(), name='add_file'),
    path('edit/<int:bb_id>/', BbEditView.as_view(), name='edit'),
    path('delete/<int:bb_id>/', BbDeleteView.as_view(), name='delete'),
    path('delete/rubric/<int:rubric_id>/', RubricDeleteView.as_view(), name='delete_rubric'),
    path('detail/<int:bb_id>/', BbDetailView.as_view(), name='detail_bb'),
    path('detail/<int:bb_id>/leave_comment', leave_comment, name='leave_comment'),
    path('client_room/', ClientRoom.as_view(), name='client_room'),
    path('authentication/', RegisterUserView.as_view(), name='register_page'),
    path('login/', BboardLoginView.as_view(), name='login'),
    path('logout/', BboardLogoutView.as_view(), name='logout'),
    path('search/bb/', process_search_results, name='search'),
]
