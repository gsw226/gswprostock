import numpy as np
import matplotlib.pyplot as plt

# 데이터 생성
np.random.seed(0)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)

# 편향(bias)을 추가
X_b = np.c_[np.ones((100, 1)), X]

# 정규방정식을 사용한 선형 회귀 계산
theta_best = np.linalg.inv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)

# 결과 출력
print("theta_best:", theta_best)

# 새로운 데이터에 대한 예측
X_new = np.array([[0], [2]])
X_new_b = np.c_[np.ones((2, 1)), X_new]
y_predict = X_new_b.dot(theta_best)

# 예측 결과 출력
print("예측 결과:", y_predict)

# 원래 데이터와 회귀선 시각화
plt.plot(X, y, "b.")
plt.plot(X_new, y_predict, "r-")
plt.xlabel("X")
plt.ylabel("y")
plt.show()