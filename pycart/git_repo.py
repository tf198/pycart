from jinja2 import Environment,FileSystemLoader
import os
from datetime import datetime
import git, renderer, utils, settings
import web, logging

logger = logging.getLogger(__name__)

def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    g = context.pop('globals', {})

    jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(g)

    #jinja_env.update_template_context(context)
    return jinja_env.get_template(template_name).render(context)

ACTION_ICONS = {'add': 'file',
                'modify': 'align-left',
                'delete': 'trash'}

# explicitly defined repos
repos = settings.REPOS.copy()

# add repo directories
logger.info("Searching for repos")
for d in getattr(settings, "REPO_DIRS", []):
    for directory, subdirs, files in os.walk(d):
        root, ext = os.path.splitext(directory)
        if ext == '.git':
            repos[root[len(d)+1:]] = directory

# remove excluded repos
for x in getattr(settings, "REPO_EXCLUDE", []):
    if x in repos:
        del(repos[x])
    
logger.info("{0} repos found".format(len(repos)))
    

class RepoMixin(object):
    template = None
    sha_type = None
    
    def GET(self, *args):
        d = self.get_context(*args)
        
        helpers = {'author_link': utils.author_link,
                   'author_gravatar': utils.author_gravatar,
                   'timesince': utils.timesince}
        
        return render_template(self.template, globals=helpers, **d)
    
    def get_repo(self, repo):
        try:
            repo_path = repos[repo]
        except KeyError:
            raise web.notfound("No repo named {0}".format(repo))
        return git.repo(repo_path)
    
    def get_base_context(self, repo, sha, path):
        d = {}
        
        self.repo = self.get_repo(repo)
        
        try:
            if sha in self.repo:
                d['ref_name'] = sha[:10]
                d['ref_link'] = sha
                self.sha = self.repo[sha]
                
            else:
                d['ref_name'] = d['ref_link'] = sha
                self.sha = git.get_branch(self.repo, sha)
        except KeyError:
            raise web.notfound('Bad SHA: {0}'.format(sha))
        
        d['repo'] = repo
        d['sha'] = self.sha.id
        d['branches'] = git.branches(self.repo)
        d['tags'] = git.tags(self.repo)
        d['sha_type'] = self.sha_type
        
        d['path'] = path.strip('/')
        d['breadcrumbs'] = d['path'].split('/') if path else []
        
        return d

class ListView(object):
    
    def GET(self):
        return render_template('list.html', repos=repos.keys())

class TreeView(RepoMixin):
    template = "tree.html"
    sha_type = 'branch'
    
    def get_context(self, repo, sha, path):
        d = self.get_base_context(repo, sha, path)
        
        path = d['path']
        listing = []
        data = None
        
        try:
            node = git.get_by_path(self.repo, self.sha, d['breadcrumbs'])
        except IndexError:
            d['error'] = "{0} does not exist in this branch".format(path)
            return d
        
        if hasattr(node, 'items'): # is directory
            last_commit = None
            for e in node.items():
                commit = git.get_commit(self.repo, self.sha, os.path.join(path, e.path))
                
                is_file = e.mode & 0100000
                
                icon = 'file' if is_file else 'folder-open'
                mode = utils.filemode(e.mode) if is_file else ""
                
                listing.append((icon,
                                e.path,
                                commit.message ,
                                mode,
                                datetime.fromtimestamp(commit.commit_time)))
                
                if last_commit is None or commit.commit_time > last_commit.commit_time:
                    last_commit = commit
                
                if e.path.lower().startswith('readme'):
                    data = self.repo[e.sha].data
                    filename = "{0}/{1}".format(d['path'], e.path)
            d['commit'] = last_commit
        else: # is a file
            data = node.data
            d['commit'] = git.get_commit(self.repo, self.sha, path)
            filename = path
        
        if data is not None:
            data, meta = renderer.render_file(filename, data)
            d['language'] = meta.get('language', 'Unknown')
            d['filename'] = filename
        
        d['data'] = data
        d['listing'] = listing
        d['inline_style'] = renderer.get_style()
                
        return d
        
class CommitView(RepoMixin):
    template = "commit.html"
    sha_type = 'commit'
    
    def get_context(self, repo, sha):
        d = self.get_base_context(repo, sha, "")
        
        try:
            commit = self.repo[sha]
        except KeyError:
            raise web.notfound("No such commit")
        
        if commit.__class__.__name__ != "Commit":
            raise web.notfound("Not a valid commit")
        
        files = []
        for change in git.get_changes(self.repo, commit):
            if change.type == 'delete':
                files.append((ACTION_ICONS.get('delete'), change.old.path, commit.parents[0], 'Deleted'))
            else:
                diff = git.unified_diff(self.repo, change.old, change.new)
                html = renderer.render_diff(diff)
                
                files.append((ACTION_ICONS.get(change.type, 'fire'), change.new.path, commit.id, html))
        
        d['inline_style'] = renderer.get_style()
                  
        d['files'] = files
        d['branch'] = commit.id
        d['commit'] = commit
        d['branch_name'] = commit.id[:10]
        
        
        return d
    
class HistoryView(RepoMixin):
    template = "history.html"
    sha_type = 'commit'
    
    def get_context(self, repo, sha, path):
        d = self.get_base_context(repo, sha, path)
        
        walker = self.repo.get_walker(include=[self.sha.id], paths=[d['path']])
        d['history'] = [ entry.commit for entry in walker ]
        
        return d
        