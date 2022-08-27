from django.http import HttpResponse
from django.template import loader
from .models import Problems,Solution,TestCases
from .models import Solution
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
import filecmp
import subprocess
import docker
from time import time
from django.conf import settings
import os



def index(request):
    problem_list = Problems.objects.all()
    context = {'problem_list': problem_list}
    return render(request, 'home/index.html', context)

def detail(request, problem_id):
    problem = get_object_or_404(Problems, pk=problem_id)
    return render(request, 'home/detail.html', {'problem': problem})


def results(request, problem_id):
    client = docker.from_env()
    Running = "running"

    if request.method=="POST":

        testcase = TestCases.objects.get(pk=problem_id)
        testcase.output=testcase.output.replace('\r\n','\n').strip()
        # inp=bytes(testcase.input,'utf-8')
        problem = get_object_or_404(Problems, pk=problem_id)

        #setting verdict to wrong by default
        verdict = "Wrong Answer" 
        res = ""
        run_time = 0

        # extract data from form
        user_code = request.POST.get('code')
        print(user_code)

        filename = str(Solution.objects.count()+1)
        file = filename + ".cpp"
        filepath = "home/templates/home" + "/" + file
        # filepath = settings.FILES_DIR + "/" + file
        code = open(filepath,"w")
        code.write(user_code)
        code.close()

        cont_name = "7fcebb72157866903e8edb236d81ea06fae6d36351db5f25f385d4b6027b7222"
        compile = f"g++ -o output {file}"
        docker_img = "gcc"

        try:
            container = client.containers.get(cont_name)
            container_state = container.attrs['State']
            container_is_running = (container_state['Status'] == Running)
            if not container_is_running:
                subprocess.run(f"docker start {cont_name}",shell=True)
        except docker.errors.NotFound:
            subprocess.run(f"docker run -dt --name {cont_name} {docker_img}",shell=True)

        #pathi="C:/Users/ADITYA/Desktop/Development/Django/preserve/home/templates/home/{file}"
        # copy/paste the .cpp file in docker container 
        subprocess.run(f"docker cp {filepath} {cont_name}:/{file}",shell=True)
        # compiling the code
        res=subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)
        # checking if the code have errors
        print(res)
        if res.stderr.decode('utf-8') != "":
            print("hi")
            verdict="CE"
        if verdict!="CE":
            # running the code on given input and taking the output in a variable in bytes
            res=subprocess.run(f"docker exec -i {cont_name} ./output",input=testcase.input.encode(),capture_output=True,shell=True)
            # removing the .cpp and .output file form the container
            subprocess.run(["docker","exec",cont_name,"rm",file])
            subprocess.run(["docker","exec",cont_name,"rm","output"])





        # user_stderr = ""
        user_stdout = ""
        # if verdict == "Compilation Error":
        #     user_stderr = cmp.stderr.decode('utf-8')
        
        if verdict == "Wrong Answer":
            # print(res.stdout)
            user_stdout = res.stdout.decode('utf-8')
            # print(user_stdout)
            # print(testcase.output)
            # print(testcase.input)
            if str(user_stdout)==str(testcase.output):
                verdict = "Accepted"
            testcase.output += '\n' # added extra line to compare user output having extra ling at the end of their output
            if str(user_stdout)==str(testcase.output):
                verdict = "Accepted"
   

        problem.solution_set.create(code=user_code, verdict=verdict, sub_time=timezone.now())
        os.remove(filepath)
    return render(request, 'home/results.html', {'question': problem})

def leaderboard(request, problem_id):
    problem = get_object_or_404(Problems, pk=problem_id)
    submission_list = problem.solution_set.order_by('-sub_time')[:10]
    context = {'submission_list': submission_list}
    return render(request, 'home/leaderboard.html', context)   
        # copy/paste the .cpp file in docker container 
        # subprocess.run(f"docker cp {filepath} {cont_name}:/{file}",shell=True)

        # # compiling the code
        # cmp = subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)
        # if cmp.returncode != 0:
        #     verdict = "Compilation Error"

        # else:
        #     # running the code on given input and taking the output in a variable in bytes
        #     start = time()
        #     try:
        #         res = subprocess.run(f"docker exec {cont_name} sh -c 'echo \"{testcase.input}\" | {exe}'",
        #                                         capture_output=True, shell=True)
        #         run_time = time()-start
        #         subprocess.run(f"docker exec {cont_name} rm {clean}",shell=True)
        #     except subprocess.TimeoutExpired:
        #         run_time = time()-start
        #         verdict = "Time Limit Exceeded"
        #         subprocess.run(f"docker container kill {cont_name}", shell=True)


        #     if verdict != "Time Limit Exceeded" and res.returncode != 0:
        #         verdict = "Runtime Error"
                