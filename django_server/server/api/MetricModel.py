class MethodMetric:
   def __init__(self, project, package, type, method, loc, cc, pc):
    
    self.project = project
    self.package = package
    self.type = type
    self.method = method
    self.loc = loc
    self.cc = cc
    self.pc = pc
    
class ClassMetric:
   def __init__(self, project, package, type, LCOM):
    
    self.project = project
    self.package = package
    self.type = type
    self.LCOM = LCOM
    
 