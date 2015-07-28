# -*- encoding: utf-8 -*-

class BreadCrumbs:
    def __init__(self):        
        self.breadcrumbs = []
        
    def add_crumb(self, crumb): 
        found = False      
        for i in self.breadcrumbs:
            if i.file_id == crumb.file_id:
                found = True
                index = self.breadcrumbs.index(i)
                del self.breadcrumbs[index+1:]
                break

        if found == False:        
            self.breadcrumbs.append(crumb)
        
        return self.breadcrumbs

    def del_crumb(self): 
        del self.breadcrumbs[:]
        return self.breadcrumbs