
import git
import logging

logging.basicConfig(format="%(levelname)-7s - %(message)s", level=logging.DEBUG)
project_url = "https://github.com/zevtyardt/asaki.git"

def lsremote(url):
    try:
        remote_refs = {}
        g = git.cmd.Git()
        for ref in g.ls_remote(url).split('\n'):
            hash_ref_list = ref.split('\t')
            remote_refs[hash_ref_list[1]] = hash_ref_list[0]
        return remote_refs
    except git.exc.GitCommandError as e:
        logging.error("failed to get the last commit")


def update():
    try:
        logging.info("check the latest version")
        repo = git.Repo(search_parent_directories=True)
        current = repo.head.object.hexsha
        if (latest := lsremote(project_url)):
            if latest.get("HEAD", current) != current:
                logging.info("updating framework")
                repo.remotes.origin.pull()
            else:
                logging.info("framework is the latest version")
    except Exception as e:
        logging.error(e)
