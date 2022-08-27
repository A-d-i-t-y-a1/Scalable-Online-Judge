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

    #setting docker client
    client = docker.from_env()
    Running = "running"

    if request.method=="POST":

        #Fetching testcases corresponding to problem
        testcase = TestCases.objects.get(pk=problem_id)
        testcase.output=testcase.output.replace('\r\n','\n').strip()
        problem = get_object_or_404(Problems, pk=problem_id)

        #setting verdict to wrong by default
        verdict = "Wrong Answer" 
        res = ""
        run_time = 0

        #file where the user code will be copied
        filename = str(Solution.objects.count()+1)
        file = filename + ".cpp"
        filepath = "home/templates/home" + "/" + file

        # extract data from form and write in file
        user_code = request.POST.get('code')
        code = open(filepath,"w")
        code.write(user_code)
        code.close()

        #container name
        cont_name = "7fcebb72157866903e8edb236d81ea06fae6d36351db5f25f385d4b6027b7222"
        #compile command for c++ file
        compile = f"g++ -o output {file}"
        #docker image
        docker_img = "gcc"

        # initialing the docker container
        try:
            container = client.containers.get(cont_name)
            container_state = container.attrs['State']
            container_is_running = (container_state['Status'] == Running)
            if not container_is_running:
                subprocess.run(f"docker start {cont_name}",shell=True)
        except docker.errors.NotFound:
            subprocess.run(f"docker run -dt --name {cont_name} {docker_img}",shell=True)

        # copy/paste the .cpp file in docker container 
        subprocess.run(f"docker cp {filepath} {cont_name}:/{file}",shell=True)

        # compiling the code
        res=subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)

        # checking if the code have errors
        if res.stderr.decode('utf-8') != "":
            verdict="CE"

        if verdict!="CE":
            # running the code on given input and taking the output in a variable in bytes
            res=subprocess.run(f"docker exec -i {cont_name} ./output",input=testcase.input.encode(),capture_output=True,shell=True)
            # removing the .cpp and .output file form the container
            subprocess.run(["docker","exec",cont_name,"rm",file])
            subprocess.run(["docker","exec",cont_name,"rm","output"])

        #removing the user code file
        os.remove(filepath)

        #user output
        user_stdout = ""

        if verdict == "Wrong Answer":
            user_stdout = res.stdout.decode('utf-8')
            if str(user_stdout)==str(testcase.output):
                verdict = "Accepted"
            testcase.output += '\n' # added extra line to compare user output having extra line at the end of their output
            if str(user_stdout)==str(testcase.output):
                verdict = "Accepted"
   

        problem.solution_set.create(code=user_code, verdict=verdict, sub_time=timezone.now())
    return render(request, 'home/results.html', {'question': problem})

def leaderboard(request, problem_id):
    problem = get_object_or_404(Problems, pk=problem_id)
    submission_list = problem.solution_set.order_by('-sub_time')[:10]
    context = {'submission_list': submission_list}
    return render(request, 'home/leaderboard.html', context)   