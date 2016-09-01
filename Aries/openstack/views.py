#-*- coding: UTF-8 -*-
from django.shortcuts import render,render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse
from openstack.middleware.login.login import Login,get_token
from openstack.middleware.image.image import Image
from openstack.middleware.flavor.flavor import Flavor
from common import json_data
from openstack.middleware.vm.vm import Vm_manage,Vm_control
from openstack.middleware.volume.volume import Volume,Volume_attach

#from
from django.views.decorators.csrf import csrf_exempt
import base64
from decimal import *
import json
import logging
openstack_log = logging.getLogger("openstack_log")



def login(request):
    ret={}
    print request.POST
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        login = Login("openstack", "baifendian2016")
        longin_token=login.user_token_login()
        proid_token=login.proid_login()
        login_proid_token=login.token_login()
        print login_proid_token
        if longin_token!=1 and proid_token!=1 and login_proid_token!=1:
            ret={"name":username,"type":2}
    json_status = json_data(ret)
    response = HttpResponse(json_status)
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Type'] = 'application/json'
    #  print response
    return response


def logout(request):
    print request.POST
    print request.GET
    aa={'aa':'bb'}
    json_status = json_data(aa)
    response = HttpResponse(json_status)
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Type'] = 'application/json'
    #  print response
    return response


def create_host(request):
    ret={}
    if request.method == 'POST':
        print request.POST
        type_name=request.POST.get('name')
        if type_name=='T1':
            ret={'cpu':"1","mem":"2","count":'0.14'}
            ret = json.dumps(ret)
            return HttpResponse(ret)
        elif type_name=="T2":
            ret={'cpu':"2","mem":"4","count":"0.24"}
            ret = json.dumps(ret)
            return HttpResponse(ret)
        elif type_name=="T3":
            ret={"cpu":"4","mem":"8","count":"0.35"}
            ret = json.dumps(ret)
            return HttpResponse(ret)

        return HttpResponseRedirect("/bfddashboard/instances/")
    return render_to_response('manage_host.html')

#    return HttpResponse('aaa')
@csrf_exempt
def instances(request):
    ret={}
    disk=[]
    sys={}
 #   print request.POST
   # ret = {'text': 'test'}
    login = Login("openstack", "baifendian2016")
    login.user_token_login()
    login.proid_login()
    login.token_login()
    vm_manage=Vm_manage()


    if request.method=="GET":
        imagess = Image()
        flavorss=Flavor()
        host_list=vm_manage.list_detail({})
        print request.GET
        currentPages=request.GET.get('currentPage')
        pageSizes =request.GET.get('pageSize')
        if currentPages and pageSizes:
            minpageSizes=(int(currentPages)-1)*int(pageSizes)
            maxpageSizes=int(currentPages)*int(pageSizes)
            print 'aaaaa',minpageSizes,maxpageSizes
            print currentPages,pageSizes
        else:
            minpageSizes=0
            maxpageSizes=0
     #   print json.dumps(host_list,indent=4)
        ret['totalList']=[]
        test_list=[]
        for host in host_list['servers'][minpageSizes:maxpageSizes]:
            print host,'.......host'
            print host_list['servers'][minpageSizes:maxpageSizes]
            sys={}
            sys['id']=host['id']
            sys['name']=host['name']
            try:
                sys['image']=imagess.show_detail(host['image']['id'])['image']['name']
            except:
                sys['image']='-'
            sys['flavor']=flavorss.show_detail(host['flavor']['id'])['flavor']['name']
            sys['created']=host['created']
            sys['status']=host['OS-EXT-STS:vm_state']
            #print host['id']
           # sys[]
            print sys
            for key,value in host['addresses'].items():
               # sys['ip']={}
                for ip in value:
                  #  sys['ip'][ip['OS-EXT-IPS:type']] =ip['addr']
                    for keys,values in ip.items():
                        if keys == "addr":
                            #print value
                            sys['ip']=values
           # print sys
            ret['totalList'].append(sys)
            test_list.append(sys)
          #  print test_list
        #    print sys
        ret['currentPage']=1
        ret['totalPageNum']=len(host_list['servers'])
    #    print ret

    if request.method=="POST":
        print request.POST
        host_method=request.POST.get('method')
        if host_method == "create":
            host_name=request.POST.get('name')
            host_count=request.POST.get('count')
            host_flavor=request.POST.get('type')
            host_image=request.POST.get('images')
            host_password='bfd123'
            host_userdata=base64.b64encode('aaa')
          #  for i in request.POST.get('brand'):
            #    disk_m='disk'+i
           #     disk.append(request.POST.get(disk_m))
            for keys,values in request.POST.items():
              #  print keys,values
                if 'disk' in keys:
                    disk.append({"size":values})
        #    print disk
            host_create=vm_manage.create_multiple(host_name,host_flavor,host_image,host_password,host_userdata,int(host_count),int(host_count),disk)
            print host_create
            if host_create!=1:
                ret['status'] = 'NO'
            else:
                ret['status'] = "YES"
           # print host_name,host_count,host_flavor,host_password,disk,host_method
        elif host_method == "start":
         #   print 'aa'
           # ret['start']='up'
            request_list=request.POST.getlist('data')[0]
            host_vm_start = Vm_control()
         #   print eval(request_list)
            for keys,values in eval(request_list).items():
                #print keys,"keys_---"
                if vm_manage.show_detail(keys)['server']['OS-EXT-STS:vm_state'] != "active":
                    host_vm_startstatus=host_vm_start.start(keys)
                    print vm_manage.show_detail(keys)['server']['OS-EXT-STS:vm_state']
                #    print host_vm_startstatus
                    if host_vm_startstatus == 1:
                        ret[values]=False
                    else:
                        ret[values]=True
                else:
                    ret[values]="active"

           # print request.POST.getlist("host_id")[0].split(',')[0]
           # host_id=request.POST.getlist("host_id")[0].split(',')[0]
         #   host_vm_start= Vm_control()
          #  print host_vm_start.start(host_id)
          #  host_vm_start.stop(host_id)


  #  return render_to_response('manage.html',{})
        elif host_method == "stop":
           # print request.POST
          #  ret={'method':'stop'}
            request_list = request.POST.getlist('data')[0]
            print request_list
            host_vm_start = Vm_control()
            for keys, values in eval(request_list).items():
                # print keys,"keys_---"
                if vm_manage.show_detail(keys)['server']['OS-EXT-STS:vm_state'] != "stopped":
                    host_vm_startstatus = host_vm_start.stop(keys)
                    print vm_manage.show_detail(keys)['server']['OS-EXT-STS:vm_state']
                    print '--------------stop'
                    #    print host_vm_startstatus
                    if host_vm_startstatus == 1:
                        ret[values] = False
                    else:
                        while True:
                            if vm_manage.show_detail(keys)['server']['OS-EXT-STS:vm_state'] == "stopped":
                                ret[values] = True
                                break
                else:
                    ret[values] = "stopped"
        elif host_method == "restart":
            type=request.POST.get('type')
            #print request_list
            if type == "restart":
                print 'restart'

            else:
                request_list = request.POST.getlist('data')[0]
                host_vm_start = Vm_control()
                for keys, values in eval(request_list).items():
                    host_vm_startstatus = host_vm_start.reboot(keys)
                    if host_vm_startstatus == 1:
                        ret[values] = False
                    else:
                        ret[values] = True

            print ret
        elif host_method == "delete":
            request_list = request.POST.getlist('data')[0]
            print request_list
            for keys,values in eval(request_list).items():
                host_vm_delete=vm_manage.delete(keys)
                print keys,values
                if host_vm_delete ==1:
                    ret[values] = False
                else:
                    ret[values] = True
        if host_method == "update":
            type=request.POST.get('type_vm')
            print "type................",type
            if type == "flavor":
                flavors=Flavor()
                host_vm_start = Vm_control()
             #   host_vm_start.resize('')
                host_id=request.POST.get('host_id')
                host_name=request.POST.get('host_name')
                type=request.POST.get('type')
                print "...........return_data"
                return_data=host_vm_start.resize(host_id,type)
                print return_data,'return_data'
                if return_data == 1:
                    ret[host_name]=False
                else:
                    ret[host_name]=True
              #  print host_vm_start.resize('b75c4e52-b031-454c-a4c6-07f83fb70a56','2')
                print host_id,host_name,type
                pass
            elif type == "image":
                host_vm_start = Vm_control()
                host_id = request.POST.get('host_id')
                host_name = request.POST.get('host_name')
                type = request.POST.get('type')
                return_data=host_vm_start.rebuild(host_id,type,host_name)
                if return_data == 1:
                    ret[host_name]=False
                else:
                    ret[host_name]=True
                pass

        elif host_method == "host_status":
            print vm_manage.result
            print ret
            pass
    json_status = json_data(ret)
    response=HttpResponse(json_status)
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Type'] = 'application/json'
  #  print response
    return  response

def images(request):
    """ 获取images"""
    sys={}
    login = Login("openstack", "baifendian2016")
    login.user_token_login()
    login.proid_login()
    login.token_login()
    print get_token()
    image = Image()
    if request.method == 'GET':
        sys['totalList'] = []
        sys['name'] = {}
      #  print json.dumps(image.list_detail(), indent=4)
        for i in image.list_detail()["images"]:
            ret={}

            if len(i['metadata']) >0:
                continue
                pass

               # ret['public'] ='NO'
               # ret['type_image']='快照'
               # sys['name'][i['id']] = i['name']
               # ret['name'] = i['name']
               # ret['type_image']=i['image_type']
               # ret['format'] = 'QCOW2'
               # ret['image_status'] = i['status']
               # ret['id'] = i['id']
               # ret['size'] = i['OS-EXT-IMG-SIZE:size']
            else:
                ret['public'] = "YES"
                ret['type_image']="镜像"
                sys['name'][i['id']] = i['name']
                ret['name'] = i['name']
                # ret['type_image']=i['image_type']
                ret['format'] = 'QCOW2'
                ret['image_status'] = i['status']
                ret['id'] = i['id']
                ret['size'] =str((round(Decimal(int(i['OS-EXT-IMG-SIZE:size']))/Decimal(1024)/Decimal(1024),2)))+'MB'
            sys['totalList'].append(ret)
        sys['currentPage'] = 1
        sys['totalPageNum'] = len(sys['totalList'])
    openstack_log.info(sys)
    json_status=json_data(sys)
    response = HttpResponse(json_status)
    response['Access-Control-Allow-Origin']='*'
    response['Content-Type']='application/json'
  #  print response1
    return response

def flavors(request):
    ret={}
    login = Login("openstack", "baifendian2016")
    login.user_token_login()
    login.proid_login()
    login.token_login()
    flavor=Flavor()
    ret['totalList'] = []
    ret['name']={}
    if request.method=='GET':
        for i in flavor.list_detail()["flavors"]:
            sys = {}
            print i
            ret['name'][i['id']] = i['name']
            sys['id']=i['id']
            sys['name']=i['name']
            sys['ram']=i['ram']
            sys['vcpus']=i['vcpus']
            sys['disk']=i['disk']
            sys['public']='yes'
            ret['totalList'].append(sys)

        ret['currentPage'] = 1
        ret['totalPageNum'] = len(ret['totalList'])

    if request.method == "POST":
        print request.POST
        host_method = request.POST.get('method')
        if host_method == 'single':
            flavor_id=request.POST.get('id')
            print flavor_id
            flavor_list=flavor.show_detail(flavor_id)
            print flavor_list
            ret['cpu']=flavor_list['flavor']['vcpus']
            ret['ram']=flavor_list['flavor']['ram']
            ret['name']=flavor_list['flavor']['name']
        if host_method=="update":

            pass


    json_status = json_data(ret)
    #print flavor.list()
  #  print json.dumps(flavor.list_detail(1),indent=4)
    response=HttpResponse(json_status)

    print type(response)
    #request['Access-Control-Allow-Headers']='Content-Type'
    response['Access-Control-Allow-Origin'] = '*'
    response["Access-Control-Allow-Headers"] = "*"
   # response["Access-Control-Allow-Methods"] = "POST,GET,PUT, DELETE"
    response['Content-Type'] = 'application/json'
   # print response1
    return response
#    return HttpResponse("fff")

def volumes(request):
    ret={}
    login = Login("openstack", "baifendian2016")
    login.user_token_login()
    login.proid_login()
    login.token_login()
    volume_s=Volume()
    vm_manage = Vm_manage()
    #print json.dumps(volume_s.list_detail(),indent=4)
    if request.method == "GET":
        ret['totalList'] = []
        volumes_list=volume_s.list_detail()
        for disk in volumes_list['volumes']:
            sys={}
          #  sys['name']=''
          #  print disk
          #  sys['name'] = test if i['displayName'] !="None" else i["id"]
            if disk['displayName'] == None:
                sys['name'] =disk['id']
            else:
                sys['name'] =disk['displayName']
            sys['id']=disk['id']
            sys['size']=disk['size']
            sys['voumetype']='ceph'
            sys['created']=disk['createdAt'].split('.')[0]
            sys['backupd']=disk['createdAt'].split('.')[0]
            sys['displayDescription']=disk['displayDescription']
          #  print "len attachments",len(disk['attachments'][0].keys())
            if len(disk['attachments'][0].keys()) == 4:
                for disk_host  in disk['attachments']:
                  #  print disk_host
                    sys['device'] = disk_host['device']
                    sys['servername']=disk_host['serverId']
            else:
                sys['device'] = ''
                sys['servername'] = ''
            #print sys
            ret['totalList'].append(sys)
        ret['currentPage'] = 1
        ret['totalPageNum'] = len(ret['totalList'])
    if request.method == "POST":
        host_method = request.POST.get('method')
        if host_method == 'attach':
            disk=request.POST.get('disk')
            host=request.POST.get('host')
            volume_attach=Volume_attach()
            ret['totalList']=[]
            for i in json.loads(disk):
                #ret[host]={}
                sys={}
                return_data=volume_attach.attach(host,i)
           #     print return_data
                if return_data == 1:
                    sys['status']=False
                else:
                    sys['device']=return_data['volumeAttachment']['device']
                    sys['servername']=vm_manage.show_detail(host)['server']['name']
                   # ret[host]['volumename']=volume_s.show_detail(i)['volume']['displayName']
                    volume_d=volume_s.show_detail(i)
                    print volume_d
                    if volume_d['volume']['displayName'] == None:
                        sys['volumename'] =volume_d['volume']['id']
                    else:
                        sys['volumename'] = volume_d['volume']['displayName']
                    sys['status']=True
                ret['totalList'].append(sys)

                print ret

 #           print json.loads(disk)[0]
   #         print request.POST.get('host')
    json_status = json_data(ret)
  #  print ret
    # print flavor.list()
    #  print json.dumps(flavor.list_detail(1),indent=4)
    response = HttpResponse(json_status)
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Type'] = 'application/json'
    return response

def test(request):
    print request.POST
    print type(request)
    print request.GET.get('test')
    aa = open('openstack/aa.txt','r').read()
    if request.method == 'POST':
        if request.POST.get("name") == 'T1':
           a1a={
		'data':{
		"totalList": [{
   			 "id": "1",
			  "name": "张三",
    		          "age": "11",
                         "country": "中国",
                          "height": "185cm",
                         "weight": "65kg",
                         "school": "六安一中",
                         "birthday": "1990-03-16"
                      }]
		},
		"code":200
	     }
           aa={"code":200,'data':{'cpu':"1","mem":"2","count":'0.12'}}
           print type(aa)
        #   aa=str(aa)
           aa=json.dumps(aa)
        if request.POST.get("name") == 'T2': 
           aa={"code":200,'data':{'cpu':"8","mem":"12","count":'0.36'}}
           print type(aa)
           aa=json.dumps(aa)
   # aa=json.loads(aa)
   # aa= eval(aa) 
   # print aa['totalList']
  #  aa=json.loads(aa)
   # aa=json.dumps(aa)
    #print aa
    response = HttpResponse(aa)
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Type'] = 'application/json'
#    return HttpResponseRedirect(reverse('index'))
    return response
  #  return render_to_response('test.html',{})

