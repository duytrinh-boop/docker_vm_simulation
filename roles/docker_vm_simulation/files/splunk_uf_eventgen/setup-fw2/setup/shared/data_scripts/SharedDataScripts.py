from platform import system

def path_set(path):
        tree = path[1:len(path)].split('/')
        if system() == 'Linux' or system() == 'Darwin':
                return path
        else:
                sep = '\\'
                win_path = 'C:'
                for branch in tree:
                        win_path += sep + branch
                return win_path

