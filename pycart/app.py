'''
Created on 25/11/2013

@author: tris
'''
import web

repo = r'/repo/([\w\/\-]+)'

urls = (
    repo + '/tree/([^/]+)/(.*)', 'git_repo.TreeView',
    repo + '/history/([^/]+)/(.*)', 'git_repo.HistoryView',
    repo + '/commit/(\w+)', 'git_repo.CommitView',
    '/', 'git_repo.ListView',
)
app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
