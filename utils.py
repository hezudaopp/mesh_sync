import hmac
import re
import os
import _file

gen_pw = lambda pw, url : hmac.new(pw, url).hexdigest()

srv = lambda server : server.serve_forever()

#def send_pathname_to_transport(self, pathname, transport):
#        for handle_request in os.listdir(pathname):
#            sourceF = os.path.join(pathname, handle_request)
#            if os.path.isfile(sourceF) or os.path.isdir(sourceF):
#                logging.info('send pathname %s to %s' % (self.source_dir_len, transport.getPeer().host))
#                transport.write(command.CMD_BEGIN + command.COMMANDS['PULL_RESPONSE'] + sourceF[self.source_dir_len:] + command.CMD_END)
#                if os.path.isdir(sourceF):
#                    self.send_pathname_to_transport(sourceF, transport)

#def ls(pattern = ""):
#    def filter_fun(dir_name):
#        if (pattern == ""):
#            return True
#        else:
#            return re.search(pattern, dir_name)
#    
#    return filter(filter_fun, os.listdir())

file_list = []
dir_list = []
filename_start = len(_file.SOURCE_DIR)+1
def get_matched_files(pattern, pathname):
    global file_list, dir_list, filename_start
    for f in os.listdir(pathname):
        ab_filename = os.path.join(pathname, f)
        if os.path.isfile(ab_filename) and re.search(pattern, f):
            file_list.append(ab_filename[filename_start:])
        elif os.path.isdir(ab_filename):
            if re.search(pattern, f):
                dir_list.append(ab_filename[filename_start:])
            get_matched_files(pattern, ab_filename)

def ls(pattern = ""):
    if not os.path.exists(_file.SOURCE_DIR):
        os.mkdir(_file.SOURCE_DIR)
    get_matched_files(pattern, _file.SOURCE_DIR)
    return (file_list, dir_list)