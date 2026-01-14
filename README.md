<h2>What is <i>CarelessVaquita</i></h2>
Careless Vaquita is an <i>open source project base template</i> with possibility to add ready to go CI/CD setup as well. 
Check out:

[ResponsibleDugong](https://github.com/mcieciora/ResponsibleDugong)

This project is strongly targeted for Python users, but with sufficient knowledge, programmers of other languages should have no problem adapting this solution to their needs, because this project only outlines good practices.
Currently supported tools and versions:

- Python 3.9.18+ 
  - requirements listed in requirements.requirements-testing.txt

- Docker 24.0.0+ & DockerCompose 2.22.0

- Unix shell 5.0.0+

- githooks 2.43.0+

- groovy 4.0.18+

<h2>About Vaquita</h2>  
Vaquita <i>(Phocoena sinus)</i> has a small body with an unusually tall, triangular dorsal fin, a rounded head, and no distinguished beak. 
The coloration is mostly grey with a darker back and a white ventral field. Prominent black patches surround its lips and eyes. 
Vaquitas reproduction time is very long as they reach sexual maturity from six years old. 
Their pregnancies last from 10 to 11 months, and vaquita calves are nursed by their mothers for 6-8 months until becoming independent. 
In 2023, it was estimated that there were as few as 10 in the wild. 
The drastic decline in vaquita population is the result of fisheries bycatch in commercial and illegal gillnets, including fisheries targeting the now-endangered Totoaba, 
shrimp, and other available fish species.
This animal was chosen as mascot for this project to raise awareness, that there are species critically endangered in the world which the exact number is not precisely 
known and the moment of extinction will likely go completely unnoticed, but commercial massive fishing that bypasses government regulations will stay intact.

![vaquita.png](doc/vaquita.PNG)

<i>source:</i> [Vaquita - Wikipedia](https://en.wikipedia.org/wiki/Vaquita)

<h2>How to setup</h2>
<h3>Step-by-step with sources</h3>   

- Fork [CarelessVaquita](https://github.com/mcieciora/CarelessVaquita). Source: [Fork a repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

- Setup git flow. Source: [Atlassian - Gitflow workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

- Generate fine-grained personal token for repository with "Read access to Contents", "Read and Write access to Pull requests", "Read and Write access to Workflows" and "Read and Write access to Commit statuses" permissions set. Source: [Fine-grained personal access token](https://github.com/settings/tokens?type=beta)

- Create repository ruleset for default and develop branches with "Restrict deletions", "Require a pull request before merging" and "Block force pushes" set. Source [Creating rulesets for a repository](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)

<h2>How to use</h2>
<h3>Branching</h3>  
By using GitFlow branching strategy you are able to diverse production branch (master/main) from around development branch (develop).
Thanks to that it is possible to have additional level of quality assurance. In general workflow of feature implementation should look as following:
1. Feature branch creation (base: develop) and feature implementation
2. Feature merge into development branch with MergeBot (more about this in the next section)
3. If all features for release are available create release branch (base: develop; target: master/main)
4. Release merge into production branch with MergeBot

<h3>Merge Bot</h3>  
MergeBot is standalone tool, written in Python, related to project, whose main task is to manage and merge currently active pull requests. With ruleset mentioned in setup part set, it is </b>NOT</b> possible for user to merge anything into develop or production branch.
To create pull request use PromoteBranch job. This pull request will be later checked periodically (on default every 5 minutes) for needed approvals from people mentioned in <i>required_reviewers</i> file. If pull request is approved and no other are in queue it will be merged into target branch.


Happy Vaquiting ;)  

<i>mcieciora</i>
