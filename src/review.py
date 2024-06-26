import os
import re

import automatic_code_review_commons as commons


def review(config):
    path_source = config['path_source']

    comments = []
    regex_id_list = config['regexId']
    todos_found = find_todo_in_files(path_source, config['extensions'])

    for file_path, line_number, line in todos_found:
        suffix = 'TODO'
        pos = line.index(suffix)
        line_only_todo = line[pos:].strip()
        description = line[pos + len(suffix):].strip()
        parts = description.split(' ')

        error = len(parts) < 1

        if len(parts) >= 1:
            has_id = False

            if len(regex_id_list) > 0:
                descr_id = parts[0]
                has_id = has_id_in_comment(regex_id_list, descr_id)
                error = not has_id

            descr_comment = ""
            start_pos = 0

            if has_id:
                start_pos = 1

            descr_comment += " ".join(parts[start_pos:])

            if len(descr_comment.replace(" ", "")) < 1:
                error = True

        if error:
            relative_path = file_path.replace(path_source, "")[1:]
            descr_comment = config['message']
            descr_comment = descr_comment.replace("${FILE_PATH}", relative_path)
            descr_comment = descr_comment.replace("${LINE_NUMBER}", str(line_number))
            descr_comment = descr_comment.replace("${TODO_CONTENT}", line_only_todo)

            comments.append(commons.comment_create(
                comment_id=commons.comment_generate_id(descr_comment),
                comment_path=relative_path,
                comment_description=descr_comment,
                comment_snipset=True,
                comment_end_line=line_number,
                comment_start_line=line_number,
            ))

    return comments


def has_id_in_comment(regex_id_list, descr_id):
    for regex in regex_id_list:
        if re.match(regex, descr_id):
            return True

    return False


def find_todo_in_files(directory, extensions):
    todos = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line_number, line in enumerate(lines, start=1):
                            line_whitout_space = line.replace(" ", "")
                            if '//TODO' in line_whitout_space or '#TODO' in line_whitout_space:
                                todos.append((file_path, line_number, line))
                except UnicodeDecodeError:
                    pass

    return todos
