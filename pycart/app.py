'''
Created on 25/11/2013

@author: tris
'''
import web

urls = (
    '/repo/(\w+)/tree/([^/]+)/(.*)', 'git_repo.TreeView',
    '/repo/(\w+)/history/([^/]+)/(.*)', 'git_repo.HistoryView',
    '/repo/(\w+)/commit/(\w+)', 'git_repo.CommitView',
    '/', 'git_repo.ListView',
)
app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()