import sys
import heapq
import time

start_time = time.time()

lines = []
with open(sys.argv[2]) as f:
    lines.extend(f.read().splitlines())

domains = lines[0].split(',')
for i in range(len(domains)):
    domains[i] = domains[i].strip()

initials = lines[1]
depth_limit = int(lines[2])
max_utilities = lines[3].split(',')
min_utilities = lines[4].split(',')

max_u = {}
min_u = {}
for u in max_utilities:
    pair = u.split(':')
    color = pair[0].strip()
    val = int(pair[1])
    max_u[color] = val
for u in min_utilities:
    pair = u.split(':')
    color = pair[0].strip()
    val = int(pair[1])
    min_u[color] = val


graph = {}
color_choice_remain = {}
for i in range(5, len(lines)):
    ss = lines[i].split(':')
    key = ss[0].strip()
    color_choice_remain[key] = set(domains)
    vals = ss[1]
    if key not in graph:
        graph[key] = set([])
    adjs = vals.split(',')
    for adj in adjs:
        graph[key].add(adj.strip())

# store what color are assigned to which states: state-color pair
maxSet = {}
minSet = {}
visited = {}
frontier = set([])

# def recover_frontier(state):
#     for adj in graph[state]:
#         if adj in frontier:
#             if state in frontier[adj]:
#                 frontier[adj].remove(state)
#             if len(frontier[adj]) == 0:
#                 frontier.pop(adj, None)
#     frontier[state] = set([])
#     for adj in graph[state]:
#         if adj in visited:
#             frontier[state].add(adj)

def add_frontier(state, cur_frontier):
    if state in cur_frontier:
        cur_frontier.remove(state)
    for adj in graph[state]:
        if adj not in cur_frontier and adj not in visited:
            cur_frontier.add(adj)
            # frontier[adj] = set([])
            # frontier[adj].add(state)

def get_colors(state):
    colors = set(domains)
    for next in graph[state]:
        if len(colors) == 0:
            # return []
            return colors
        if next in visited:
            if visited[next] == 1:
                if maxSet[next] in colors:
                    colors.remove(maxSet[next])
            elif visited[next] == 2:
                if minSet[next] in colors:
                    colors.remove(minSet[next])
    # res = []
    # for color in colors:
    #     heapq.heappush(res, color)
    return colors

def add_color(state, color, cur_color_choices):
    for adj in graph[state]:
        if color in cur_color_choices[adj]:
            cur_color_choices[adj].remove(color)

# def recover_color(state):
#     for adj in graph[state]:
#         colors = get_colors(adj)
#         color_choice_remain[adj] = colors


# assign the initial assignments
actions = initials.split(',')
for action in actions:
    vals = action.split(':')
    state = vals[0].strip()
    assigment_and_player = vals[1].split('-')
    assigment = assigment_and_player[0].strip()
    player = int(assigment_and_player[1])
    if player == 1:
        maxSet[state] = assigment
        visited[state] = 1
    elif player == 2:
        minSet[state] = assigment
        visited[state] = 2
    add_frontier(state, frontier)
    add_color(state, assigment, color_choice_remain)

filename = sys.argv[2].split('.')[0]
fo = open(filename + '_output.txt', 'w')


def eval():
    max_sum = 0
    min_sum = 0
    for key in maxSet:
        max_sum += max_u[maxSet[key]]
    for key in minSet:
        min_sum += min_u[minSet[key]]
    return max_sum - min_sum

def copy_dict(d):
    res = {}
    for key in d:
        res[key] = d[key].copy()
    return res


def log(fo, state, color, depth, value, alpha, beta):
    fo.write(state)
    fo.write(', ')
    fo.write(color)
    fo.write(', ')
    fo.write(str(depth))
    fo.write(', ')
    fo.write(str(value))
    fo.write(', ')
    fo.write(str(alpha))
    fo.write(', ')
    fo.write(str(beta))
    fo.write('\n')


def max_value(state, depth, alpha, beta, color, cur_frontier, cur_color_choices):
    res_color = color
    res_node = state
    v = -float('Inf')
    visited[state] = 2
    minSet[state] = color
    add_frontier(state, cur_frontier)
    add_color(state, color, cur_color_choices)
    has = False
    for name in cur_frontier:
        if len(cur_color_choices[name]) > 0:
            has = True
    if depth == depth_limit or not has:
        val = eval()
        visited.pop(state, None)
        minSet.pop(state, None)
        log(fo, state, color, depth, val, alpha, beta)
        return res_node, res_color, val
    else:
        log(fo, state, color, depth, v, alpha, beta)
    cur_q = []
    for name in cur_frontier:
        heapq.heappush(cur_q, name)
    while len(cur_q) > 0:
        next = heapq.heappop(cur_q)
        next_colors = cur_color_choices[next]
        next_colors_q = []
        for ccc in next_colors:
            heapq.heappush(next_colors_q, ccc)
        while len(next_colors_q) > 0:
            c = heapq.heappop(next_colors_q)
            temp_node, temp_color, temp_v = min_value(next, depth + 1, alpha, beta, c, cur_frontier.copy(), copy_dict(cur_color_choices))
            v = max(v, temp_v)
            old_alpha = alpha
            if v > alpha:
                res_node = next
                res_color = c
            alpha = max(v, alpha)
            if v >= beta:
                log(fo, state, color, depth, v, old_alpha, beta)
            else:
                log(fo, state, color, depth, v, alpha, beta)
            if v >= beta:
                visited.pop(state, None)
                minSet.pop(state, None)
                return res_node, res_color, v
    visited.pop(state, None)
    minSet.pop(state, None)
    return res_node, res_color, v




def min_value(state, depth, alpha, beta, color, cur_frontier, cur_color_choices):
    res_color = color
    res_node = state
    v = float('Inf')
    visited[state] = 1
    maxSet[state] = color
    add_frontier(state, cur_frontier)
    add_color(state, color, cur_color_choices)
    has = False
    for name in cur_frontier:
        if len(cur_color_choices[name]) > 0:
            has = True
    if depth == depth_limit or not has:
        val = eval()
        visited.pop(state, None)
        maxSet.pop(state, None)
        log(fo, state, color, depth, val, alpha, beta)
        return res_node, res_color, val
    else:
        log(fo, state, color, depth, v, alpha, beta)
    cur_q = []
    for name in cur_frontier:
        heapq.heappush(cur_q, name)
    while len(cur_q) > 0:
        next = heapq.heappop(cur_q)
        next_colors = cur_color_choices[next]
        next_colors_q = []
        for ccc in next_colors:
            heapq.heappush(next_colors_q, ccc)
        while len(next_colors_q) > 0:
            has = True
            c = heapq.heappop(next_colors_q)
            temp_node, temp_color, temp_v = max_value(next, depth + 1, alpha, beta, c, cur_frontier.copy(), copy_dict(cur_color_choices))
            v = min(v, temp_v)
            old_beta = beta
            if v < beta:
                res_node = next
                res_color = c
            beta = min(v, beta)
            if v <= alpha:
                log(fo, state, color, depth, v, alpha, old_beta)
            else:
                log(fo, state, color, depth, v, alpha, beta)
            if v <= alpha:
                visited.pop(state, None)
                maxSet.pop(state, None)
                return res_node, res_color, v
    visited.pop(state, None)
    maxSet.pop(state, None)
    return res_node, res_color, v

last_action = actions[len(actions) - 1]
start_node = last_action.split(':')[0].strip()
start_color = last_action.split(':')[1].split('-')[0].strip()
final_node, final_color, final_val = max_value(start_node, 0, -float('inf'), float('inf'), start_color, frontier.copy(), color_choice_remain.copy())
print final_node, final_color, final_val
fo.write(final_node)
fo.write(', ')
fo.write(final_color)
fo.write(', ')
fo.write(str(final_val))

print time.time() - start_time