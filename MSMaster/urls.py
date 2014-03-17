from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'MSMaster.views.home', name='home'),
    # url(r'^MSMaster/', include('MSMaster.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$',       'main.views.login'),
    url(r'^accounts/logout/$',      'main.views.logout'),
    url(r'^get_username/$',         'main.views.get_username'),
    url(r'^$',                      'main.views.main'),
    url(r'^tree/$',                 'main.views.tree'),
    url(r'^get_ms_list/([^/]+)/$',              'MS.views.get_ms_list'),
    url(r'^show_ms_info/([^/]+)/$',             'MS.views.show_ms_list'),
    url(r'^sync_ms_db/([^/]+)/$',               'MS.views.sync_ms_db'),
    url(r'^sync_ms_status/([^/]+)/$',           'MS.views.sync_ms_status'),
    url(r'^ms_add_hot_tasks/([^/]+)/$',         'MS.views.ms_add_hot_tasks'),
    url(r'^ms_delete_cold_tasks/([^/]+)/$',     'MS.views.ms_delete_cold_tasks'),
    url(r'^get_room_list/([^/]+)/$',            'room.views.get_room_list'),
    url(r'^show_room_info/([^/]+)/$',           'room.views.show_room_list'),
    url(r'^sync_room_db/([^/]+)/$',             'room.views.sync_room_db'),
    url(r'^sync_room_status/([^/]+)/$',         'room.views.sync_room_status'),
    url(r'^add_hot_tasks/([^/]+)/$',            'room.views.add_hot_tasks'),
    url(r'^delete_cold_tasks/([^/]+)/$',        'room.views.delete_cold_tasks'),
    url(r'^auto_distribute_tasks/([^/]+)/$',    'room.views.auto_distribute_tasks'),
    url(r'^auto_delete_tasks/([^/]+)/$',        'room.views.auto_delete_tasks'),
    url(r'^room_in_virtual_room/([^/]+)/$',     'room.views.room_in_virtual_room'),
    url(r'^add_virtual_room/([^/]+)/$',         'virtual_room.views.add_virtual_room'),
    url(r'^modify_virtual_room/([^/]+)/$',      'virtual_room.views.modify_virtual_room'),
    url(r'^delete_virtual_room/([^/]+)/$',      'virtual_room.views.delete_virtual_room'),
    url(r'^stat_virtual_room/([^/]+)/$',        'virtual_room.views.stat_virtual_room'),
    url(r'^get_virtual_room_list/([^/]+)/$',    'virtual_room.views.get_virtual_room_list'),
    url(r'^show_virtual_room_detail/([^/]+)/$', 'virtual_room.views.show_virtual_room_detail'),
    url(r'^virtual_room_add_tasks/([^/]+)/$',   'virtual_room.views.virtual_room_add_tasks'),
    url(r'^virtual_room_delete_tasks/([^/]+)/$','virtual_room.views.virtual_room_delete_tasks'),
    url(r'^get_task_list/([^/]+)/$',            'task.views.get_task_list'),
    url(r'^sync_hash_db/([^/]+)/$',             'task.views.sync_hash_db'),
    url(r'^sync_pay_medias/([^/]+)/$',          'task.views.sync_pay_medias'),
    url(r'^down_hot_tasks/([^/]+)/$',           'task.views.down_hot_tasks'),
    url(r'^down_cold_tasks/([^/]+)/$',          'task.views.down_cold_tasks'),
    url(r'^show_task_info/([^/]+)/$',           'task.views.show_task_list'),
    url(r'^upload_hits_num/([^/]+)/$',          'task.views.upload_hits_num'),
    url(r'^calc_temperature/([^/]+)/$',         'task.views.calc_temperature'),
    url(r'^evaluate_temperature/([^/]+)/$',     'task.views.evaluate_temperature'),
    url(r'^get_parameters/([^/]+)/$',           'task.views.get_parameters'),
    url(r'^set_parameters/([^/]+)/$',           'task.views.set_parameters'),
    url(r'^calc_hot_mean_hits_num/([^/]+)/$',   'task.views.calc_hot_mean_hits_num'),
    url(r'^test_insert/([^/]+)/$',              'task.views.test_insert'),
    url(r'^test_select/([^/]+)/$',              'task.views.test_select'),
    url(r'^get_operation_list/([^/]+)/$',       'operation.views.get_operation_list'),
    url(r'^show_operation_info/([^/]+)/$',      'operation.views.show_operation_list'),
    url(r'^do_selected_operations/([^/]+)/$',   'operation.views.do_selected_operations'),
    url(r'^do_all_operations/([^/]+)/$',        'operation.views.do_all_operations'),
)

from django.conf import settings
if settings.DEBUG is False:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
   )
