def solution(grid):
    answer = [ ]
    for i in range(5):
        if i%2 == 1:
            answer.append(min(grid[i]))
        else:
            answer.append(max(grid[i]))
    return answer

grid = [[20, 8, 29, 4, 3], [10, 26, 28, 49, 27], [45, 5, 19, 38, 25], [9, 31, 36,
11, 35], [12, 40, 24, 33, 6]]
ret = solution(grid)
print("solution 함수의 반환 값은", ret, "입니다.")