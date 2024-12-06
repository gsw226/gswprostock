def add_candidates():
    candidates = []
    num_candidates = int(input("후보자 수를 입력하세요: "))
    for _ in range(num_candidates):
        candidate_name = input("후보자의 이름을 입력하세요: ")
        if candidate_name in candidates:
            print(f"{candidate_name}은(는) 이미 후보자입니다.")
        else:
            candidates.append(candidate_name)
    return candidates

def collect_votes(candidates):
    num_voters = int(input("투표자 수를 입력하세요: "))
    votes = {candidate: 0 for candidate in candidates}
    print("후보자 목록:")
    c = 1
    for candidate in candidates:
        print(f"{c}. {candidate}")
        c+=1  #c=c+1

    for a in range(num_voters):
        while True:
            try:
                vote = int(input("투표할 후보자의 번호를 입력하세요: ")) - 1
                if 0 <= vote < len(candidates):
                    votes[candidates[vote]] += 1
                    break
                else:
                    print("잘못된 후보자 번호입니다. 다시 시도해주세요.")
            except ValueError:
                print("잘못된 입력입니다. 번호를 입력해주세요.")
    
    return votes

def show_results(votes):
    print("\n투표 결과:")
    for candidate, vote_count in votes.items():
        print(f"{candidate}: {vote_count}표")

    winner = max(votes, key=votes.get)
    print(f"\n승자는 {winner}로, {votes[winner]}표를 받았습니다.")

candidates = add_candidates()
votes = collect_votes(candidates)
show_results(votes)