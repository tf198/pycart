from dulwich.repo import Repo
from dulwich.patch import write_object_diff

# Going old school procedural
# Most of the methods will return the bound object 

def repo(path):
    return Repo(path)

def branches(repo):
    return repo.refs.keys('refs/heads')

def tags(repo):
    return repo.refs.keys('refs/tags')

def get_ref(repo, name):
    try:
        return repo[repo.refs[name]]
    except KeyError:
        raise KeyError("No ref named '{0}'".format(name))
    
def get_branch(repo, name):
    if name == 'HEAD':
        return get_ref(repo, name)
    return get_ref(repo, 'refs/heads/' + name)

def get_tag(repo, tag):
    return get_ref(repo, 'refs/tags/' + tag)

def get_tree(repo, commit):
    return repo[commit.tree]

def get_by_path(repo, commit, parts):
    
    node = get_tree(repo, commit)
    
    # need to filter the tree entries by their path attribute
    def select_by_path(s, match):
        for i in s:
            if i.path == match: return i
        raise IndexError("No match for path '{0}'".format(match))
    
    # descend the tree
    for p in parts:
        entry = select_by_path(node.items(), p)
        node = repo[entry.sha]
        
    return node

def get_commit(repo, branch, path):
    w = repo.get_walker(include=[branch.id], paths=[path], max_entries=1)
    try:
        return iter(w).next().commit
    except StopIteration:
        return branch
    
def get_changes(repo, commit):
    w = repo.get_walker(include=[commit.id], max_entries=1)
    try:
        return iter(w).next().changes()
    except StopIteration:
        return []
    
def unified_diff(repo, old, new):
    import StringIO
    s = StringIO.StringIO()
    
    write_object_diff(s, repo, old, new)
    
    return s.getvalue()
    