//
// Created by Zhuoxun Yang on 3/25/2025.
//

#ifndef SZ_ParamTuning_HPP
#define SZ_ParamTuning_HPP

#include "SZ3/def.hpp"
#include "SZ3/quantizer/Quantizer.hpp"
#include "SZ3/utils/Config.hpp"
#include "SZ3/utils/FileUtil.hpp"
#include "SZ3/utils/Iterator.hpp"
#include "SZ3/utils/MemoryUtil.hpp"
#include "SZ3/utils/Timer.hpp"
#include <stdlib.h>

#include <vector>
#include <stdexcept>
#include <cmath>
#include <algorithm> // std::swap
#include <iostream>
// 如有需要可启用 OpenMP
// #ifdef _OPENMP
#include <omp.h>
// #endif

// 计算向量点积
double dotProduct(const std::vector<double>& a, const std::vector<double>& b) {
    if(a.size() != b.size())
        throw std::runtime_error("Vectors must be of same length.");
    double sum = 0.0;
    for (size_t i = 0; i < a.size(); i++) {
        sum += a[i] * b[i];
    }
    return sum;
}

// 用高斯消元法求解 n×n 的线性方程组 M * x = b
std::vector<double> solveLinearSystem(std::vector<double>& M, std::vector<double>& b, int n) {
    // 前向消元
    for (int i = 0; i < n; i++) {
        // 选取主元
        int pivotRow = i;
        double pivotVal = std::fabs(M[i*n + i]);
        for (int r = i + 1; r < n; r++) {
            double val = std::fabs(M[r*n + i]);
            if (val > pivotVal) {
                pivotVal = val;
                pivotRow = r;
            }
        }
        if (pivotVal < 1e-12)
            throw std::runtime_error("Matrix is singular or ill-conditioned.");
        if (pivotRow != i) {
            for (int j = 0; j < n; j++) {
                std::swap(M[i*n + j], M[pivotRow*n + j]);
            }
            std::swap(b[i], b[pivotRow]);
        }
        // 消元
        for (int r = i + 1; r < n; r++) {
            double factor = M[r*n + i] / M[i*n + i];
            for (int j = i; j < n; j++) {
                M[r*n + j] -= factor * M[i*n + j];
            }
            b[r] -= factor * b[i];
        }
    }
    // 回代求解
    std::vector<double> x(n, 0.0);
    for (int i = n - 1; i >= 0; i--) {
        double sum = b[i];
        for (int j = i + 1; j < n; j++) {
            sum -= M[i*n + j] * x[j];
        }
        x[i] = sum / M[i*n + i];
    }
    return x;
}

/**
 * @brief 计算岭回归（正则化最小二乘）的闭式解。
 *
 *  输入：
 *    - X: 大小为 N × k 的特征矩阵，每一行为一个 k 维向量。
 *    - y: 大小为 N 的目标向量。
 *    - lambda: 正则化参数（仅对 w 部分正则化，不对截距 s 正则化）。
 *
 *  输出：
 *    返回一个长度为 k+1 的向量，其中前 k 个元素为最优的 w，
 *    最后一个元素为最优的 s。
 */
std::vector<double> computeClosedFormRidge(const std::vector<std::vector<double>>& X,
                                           const std::vector<double>& y,
                                           double lambda)
{
    int N = X.size();
    if (N == 0)
        throw std::runtime_error("No samples provided.");
    int k = X[0].size();
    int d = k + 1; // 增广后维度

    // 初始化 M = A^T A 和 b_vec = A^T y，其中 A 的每一行为 (X[i], 1)
    std::vector<double> M(d * d, 0.0);
    std::vector<double> b_vec(d, 0.0);
    
    for (int i = 0; i < N; i++) {
        if (X[i].size() != static_cast<size_t>(k))
            throw std::runtime_error("Inconsistent sample dimension.");
        // 构造增广向量 a = [X[i][0], X[i][1], ..., X[i][k-1], 1]
        std::vector<double> a(d, 0.0);
        for (int j = 0; j < k; j++) {
            a[j] = X[i][j];
        }
        a[k] = 1.0;
        // 累加 A^T A 和 A^T y
        for (int p = 0; p < d; p++) {
            b_vec[p] += a[p] * y[i];
            for (int q = 0; q < d; q++) {
                M[p*d + q] += a[p] * a[q];
            }
        }
    }
    
    // 加上正则化项：对 w 的部分（前 k 个分量）在对角线上加 lambda
    for (int i = 0; i < k; i++) {
        M[i*d + i] += lambda;
    }
    // 注意：截距 s（最后一个分量）不正则化，所以 M[k*d + k] 保持不变。

    // 复制 M 和 b_vec，因为 solveLinearSystem 会修改它们
    std::vector<double> M_copy = M;
    std::vector<double> b_copy = b_vec;

    // 求解 (M)x = b_vec，x 为增广参数 [w; s]
    std::vector<double> sol = solveLinearSystem(M_copy, b_copy, d);
    return sol;
}

/**
 * @brief 先进行一次回归，过滤掉残差大于 threshold 的点，再做一次回归，返回最终回归的参数。
 *
 *  输入：
 *    - X: 大小为 N×k 的特征矩阵，每一行为一个 k 维向量。
 *    - y: 大小为 N 的目标向量。
 *    - lambda: 正则化参数（仅对 w 正则化，不对 s 正则化）。
 *    - threshold: 过滤阈值，若 |f(v)-y| > threshold 的点将被剔除。
 *
 *  输出：
 *    返回一个长度为 k+1 的向量，其中前 k 个元素为最终的 w，最后一个元素为最终的 s。
 */
int robustRidgeRegression(const std::vector<std::vector<double>>& X,
                                          const std::vector<double>& y,
                                          std::vector<double>& result,
                                          double lambda,
                                          double threshold)
{
    int N = X.size();
    std::cout << "X size: " << N << std::endl;
    if (N <= 4)
        return 1;
        // throw std::runtime_error("No training samples provided.");
    int k = X[0].size();

    // 第一次回归：利用所有数据计算初步参数
    std::vector<double> sol = computeClosedFormRidge(X, y, lambda);
    // 分离 w 与 s（sol 的前 k 个为 w，最后一个为 s）
    std::vector<double> w(sol.begin(), sol.begin() + k);
    double s = sol[k];

    // 过滤：保留 |f(v) - y| <= threshold 的样本
    std::vector<std::vector<double>> X_filtered;
    std::vector<double> y_filtered;
    for (int i = 0; i < N; i++) {
        double pred = dotProduct(X[i], w) + s;
        double error = std::fabs(pred - y[i]);
        if (error <= threshold) {
            X_filtered.push_back(X[i]);
            y_filtered.push_back(y[i]);
        }
    }
    if (X_filtered.empty())
        return 1;
        // throw std::runtime_error("No samples remain after filtering with the given threshold.");
    std::cout << "X_filtered size: " << X_filtered.size() << std::endl;

    // 第二次回归：在过滤后的数据上重新回归
    std::vector<double> sol_filtered = computeClosedFormRidge(X_filtered, y_filtered, lambda);
    result = sol_filtered;
    return 0;
}

namespace SZ3 {

/**
 * @brief add the contribution of sample(a, b) to matrix M and vector v
 *
 * @param a  intput vector a with size k
 * @param b  scalar
 * @param M  matrix that accumulately record A^T A (with 1d memory alignment). The size must be k*k
 * @param v  
 * @param k  
 */
void accumulateOneSample(const std::vector<double>& a,
                         double b,
                         std::vector<double>& M,
                         std::vector<double>& v,
                         int k)
{
    if (static_cast<int>(a.size()) != k) {
        throw std::runtime_error("Size of vector a does not match k.");
    }
    if (static_cast<int>(v.size()) != k) {
        throw std::runtime_error("Size of vector v does not match k.");
    }
    if (static_cast<int>(M.size()) != k*k) {
        throw std::runtime_error("Size of matrix M does not match k*k.");
    }

    // M += a * a^T
    for (int i = 0; i < k; ++i) {
        for (int j = 0; j < k; ++j) {
            M[i*k + j] += a[i] * a[j];
        }
    }
    // v += b * a
    for (int i = 0; i < k; ++i) {
        v[i] += b * a[i];
    }
}

void Predictor(const std::vector<double>& a,
                         double b,
                         int k) 
{
    if (static_cast<int>(a.size()) != k) {
        throw std::runtime_error("Size of vector a does not match k.");
    }

    std::vector<double> M, v;
    M.resize(k * k, 0);
    v.resize(k, 0);



}



/**
 * @brief 在不使用外部库的情况下，求解 (M + lambda I) x = v
 *        其中 M 为 k*k，v 为 k，均以一维数组或向量表示
 *
 * @param M         累加得到的 (A^T A)，大小 k*k (row-major)，会在函数内被修改
 * @param v         累加得到的 (A^T b)，大小 k，函数内会被修改
 * @param k         矩阵/向量的维度
 * @param lambdaVal 正则化系数 (lambda)
 * @return std::vector<double> 解向量 x，大小为 k
 */
std::vector<double> solveWithRegularization(std::vector<double>& M,
                                           std::vector<double>& v,
                                           int k,
                                           double lambdaVal)
{
    if (static_cast<int>(M.size()) != k*k) {
        throw std::runtime_error("Matrix M size != k*k.");
    }
    if (static_cast<int>(v.size()) != k) {
        throw std::runtime_error("Vector v size != k.");
    }

    // 1) 在 M 对角线加上 lambda
    //    即 M[i,i] += lambda
    for (int i = 0; i < k; ++i) {
        M[i*k + i] += lambdaVal;
    }

    // 2) 用 高斯消去法(带部分主元选择) 解 M x = v
    //    (a) 前向消去 (Forward Elimination)
    for (int i = 0; i < k; ++i)
    {
        // 在第 i 列，从第 i 行到最后，找到绝对值最大的主元 pivot_row
        int pivotRow = i;
        double pivotVal = std::fabs(M[i*k + i]);
        for (int r = i+1; r < k; ++r) {
            double val = std::fabs(M[r*k + i]);
            if (val > pivotVal) {
                pivotVal = val;
                pivotRow = r;
            }
        }

        // 如果主元近乎 0，说明矩阵奇异或数值非常不稳定
        if (pivotVal < 1e-14) {
            throw std::runtime_error("Matrix is singular or ill-conditioned.");
        }

        // 如 pivotRow != i，则交换行 pivotRow 与 i
        if (pivotRow != i) {
            // 交换 M 中的两行
            for (int c = 0; c < k; ++c) {
                std::swap(M[i*k + c], M[pivotRow*k + c]);
            }
            // 交换 v 中对应元素
            std::swap(v[i], v[pivotRow]);
        }

        // 用第 i 行消去下面的行
        for (int r = i+1; r < k; ++r) {
            double ratio = M[r*k + i] / M[i*k + i];
            // r 行的每个元素都要减去 ratio * (i 行的对应元素)
            for (int c = i; c < k; ++c) {
                M[r*k + c] -= ratio * M[i*k + c];
            }
            v[r] -= ratio * v[i];
        }
    }

    //  (b) 回代 (Back Substitution)
    std::vector<double> x(k, 0.0);
    for (int i = k-1; i >= 0; --i) {
        double sumVal = v[i];
        for (int c = i+1; c < k; ++c) {
            sumVal -= M[i*k + c] * x[c];
        }
        // 这里如果对角线元素过小，依然会出问题
        // 但我们已经在前向时做了 pivoting 一定程度上缓解
        if (std::fabs(M[i*k + i]) < 1e-14) {
            throw std::runtime_error("Zero pivot encountered in back substitution.");
        }
        x[i] = sumVal / M[i*k + i];
    }

    return x;
}





/**
 * @brief 用信息势作为损失函数（最小误差熵），利用 mini-batch 随机采样来近似梯度下降
 *        模型为 f(v)=v·w+s
 *
 * @param X            训练数据，每一行为一个 k 维向量 v
 * @param y            训练数据对应的标量目标值，大小为 N
 * @param w            模型参数 w（k 维向量），函数内更新
 * @param s            模型偏置 s（标量），注意信息势对 s 不敏感，通常可固定或辅以其他损失
 * @param sigma        高斯核宽度参数 σ（控制核的平滑度）
 * @param learningRate 学习率
 * @param iterations   迭代次数
 */
void gradientDescentInformationPotential(const std::vector<std::vector<double>>& X,
                                                    const std::vector<double>& y,
                                                    std::vector<double>& w,
                                                    double s,
                                                    double sigma,
                                                    double learningRate,
                                                    int iterations)
{
    int batchPairs = 256;
    int N = X.size();
    if (N == 0)
        throw std::runtime_error("No training samples provided.");
    int k = X[0].size();
    if (w.size() != static_cast<size_t>(k))
        throw std::runtime_error("Size of w must equal feature dimension k.");

    // 用于随机数生成
    std::srand(static_cast<unsigned int>(std::time(nullptr)));

    // 临时存放每个样本的误差 e_i = v_i·w + s - y_i
    std::vector<double> errors(N, 0.0);

    for (int iter = 0; iter < iterations; iter++) {
        // 1. 计算所有样本的误差
        for (int i = 0; i < N; i++) {
            if (X[i].size() != static_cast<size_t>(k))
                throw std::runtime_error("All feature vectors must have the same length.");
            errors[i] = dotProduct(X[i], w) + s - y[i];
        }

        // 2. 随机采样 batchPairs 个样本对，累加梯度和损失
        std::vector<double> grad_w(k, 0.0);
        double loss = 0.0;

        // 采用 OpenMP 并行化采样求和（每次迭代内各对相对独立）
        #pragma omp parallel for reduction(+:loss)
        for (int b = 0; b < batchPairs; b++) {
            // 随机采样两个样本索引
            int i = std::rand() % N;
            int j = std::rand() % N;
            double diff = errors[i] - errors[j];
            double kernel = std::exp(- (diff * diff) / (4 * sigma * sigma));
            // 累加损失
            loss -= kernel;

            double factor = (diff) / (2 * sigma * sigma) * kernel;
            // 由于 grad_w 是一个数组，需要保护更新（采用临界区）
            #pragma omp critical
            {
                for (int d = 0; d < k; d++) {
                    grad_w[d] += factor * (X[i][d] - X[j][d]);
                }
            }
        }
        // 归一化梯度和损失
        loss /= batchPairs;
        for (int d = 0; d < k; d++) {
            grad_w[d] /= batchPairs;
        }

        // 每隔一定迭代数输出损失
        if ((iter + 1) % 100 == 0)
            std::cout << "Iteration " << iter+1 << ", Loss = " << loss << std::endl;

        // 3. 更新参数 w（s 在信息势中梯度为 0，此处不更新）
        for (int d = 0; d < k; d++) {
            w[d] -= learningRate * grad_w[d];
        }
    }
}
// /**
//  * @brief 用信息势作为损失函数，对模型 f(v)=v·w+s 进行梯度下降优化，并自动调整学习率
//  *
//  * 模型预测为 f(v)= dot(v, w) + s，其中 s 在本例中保持不变（信息势对 s 的梯度为 0）。
//  *
//  * 损失函数定义为：
//  *   J = - (1/N^2)*sum_{i,j} exp(- (e_i - e_j)^2/(4σ^2))
//  * 其中 e_i = dot(v_i, w) + s - y_i.
//  *
//  * 每隔 checkInterval 次迭代检查损失改善情况，若改善不足则将学习率乘以 lr_decay_factor。
//  *
//  * @param X            训练数据，每一行为一个 k 维向量
//  * @param y            训练数据对应的标量目标值，大小为 N
//  * @param w            模型参数 w（k 维向量），函数内更新
//  * @param s            模型偏置 s（标量），保持不变
//  * @param sigma        高斯核宽度参数 σ
//  * @param learningRate 初始学习率（会在过程中自动调整）
//  * @param iterations   总迭代次数
//  */
// // void gradientDescentInformationPotential(const std::vector<std::vector<double>>& X,
// //                                                    const std::vector<double>& y,
// //                                                    std::vector<double>& w,
// //                                                    double s,
// //                                                    double sigma,
// //                                                    double learningRate,
// //                                                    int iterations)
// {
//     int N = X.size();
//     if (N == 0)
//         throw std::runtime_error("No training samples provided.");
//     int k = X[0].size();
//     if (w.size() != static_cast<size_t>(k))
//         throw std::runtime_error("Size of w must equal feature dimension k.");

//     std::vector<double> errors(N, 0.0);

//     // 自动调整学习率参数
//     int checkInterval = 30;         // 每100次迭代检查一次
//     double threshold = 1e-4;           // 若损失改善小于此阈值则降低学习率
//     double lr_decay_factor = 0.5;      // 学习率衰减因子
//     double prevLoss = 1e12;            // 初始设一个很大的prevLoss

//     for (int iter = 0; iter < iterations; iter++) {
//         // 1. 计算每个样本的误差 e_i = dot(v_i, w) + s - y_i
//         for (int i = 0; i < N; i++) {
//             if (X[i].size() != static_cast<size_t>(k))
//                 throw std::runtime_error("All feature vectors must have the same length.");
//             errors[i] = dotProduct(X[i], w) + s - y[i];
//         }

//         // 2. 计算损失和对 w 的梯度
//         double loss = 0.0;
//         std::vector<double> grad_w(k, 0.0);

//         // 对于每个样本对 (i, j)
//         for (int i = 0; i < N; i++) {
//             for (int j = 0; j < N; j++) {
//                 double diff = errors[i] - errors[j];
//                 double kernel = std::exp(- (diff * diff) / (4 * sigma * sigma));
//                 loss -= kernel;  // 累加负的核值
//                 double factor = (diff) / (2 * sigma * sigma) * kernel;
//                 for (int d = 0; d < k; d++) {
//                     grad_w[d] += factor * (X[i][d] - X[j][d]);
//                 }
//             }
//         }
//         // 归一化
//         loss /= (N * N);
//         for (int d = 0; d < k; d++) {
//             grad_w[d] /= (N * N);
//         }

//         // 3. 自动调学习率：每 checkInterval 次迭代检查一次
//         if ((iter + 1) % checkInterval == 0) {
//             std::cout << "Iteration " << iter+1 << ", Loss = " << loss << ", Learning Rate = " << learningRate << std::endl;
//             if ((prevLoss - loss) < threshold) {
//                 learningRate *= lr_decay_factor;
//                 std::cout << "Loss improvement less than threshold. Reducing learning rate to " << learningRate << std::endl;
//             }
//             prevLoss = loss;
//         }

//         // 4. 更新 w
//         for (int d = 0; d < k; d++) {
//             w[d] -= learningRate * grad_w[d];
//         }
//         if(1.0 - loss < 1e-4) return;
//     }
// }

// /**
//  * @brief 用信息势（最小误差熵）作为损失函数，对模型 f(v)=v·w+s 用梯度下降进行优化
//  *
//  * @param X            训练数据，每一行为一个 k 维向量 v
//  * @param y            训练数据对应的标量目标值，大小为 N
//  * @param w            模型参数 w（k 维向量），函数内更新
//  * @param s            模型偏置 s（标量），由于信息势对 s 不敏感，这里保持不变
//  * @param sigma        高斯核宽度参数 σ（控制核的平滑度）
//  * @param learningRate 学习率
//  * @param iterations   迭代次数
//  */
// void gradientDescentInformationPotential(const std::vector<std::vector<double>>& X,
//                                            const std::vector<double>& y,
//                                            std::vector<double>& w,
//                                            double s,
//                                            double sigma,
//                                            double learningRate,
//                                            int iterations)
// {
//     int N = X.size();
//     if (N == 0)
//         throw std::runtime_error("No training samples provided.");
//     int k = X[0].size();
//     if (w.size() != static_cast<size_t>(k))
//         throw std::runtime_error("Size of w must equal feature dimension k.");

//     // 临时存放每个样本的误差 e_i = v_i·w + s - y_i
//     std::vector<double> errors(N, 0.0);

//     for (int iter = 0; iter < iterations; iter++) {
//         // 1. 计算所有样本的误差
//         for (int i = 0; i < N; i++) {
//             if (X[i].size() != static_cast<size_t>(k))
//                 throw std::runtime_error("All feature vectors must have the same length.");
//             errors[i] = dotProduct(X[i], w) + s - y[i];
//         }

//         // 2. 计算损失和梯度
//         double loss = 0.0;
//         std::vector<double> grad_w(k, 0.0);

//         // 对于每个样本对 (i, j)
//         for (int i = 0; i < N; i++) {
//             for (int j = 0; j < N; j++) {
//                 double diff = errors[i] - errors[j];
//                 double kernel = std::exp(- (diff * diff) / (4 * sigma * sigma));
//                 loss -= kernel; // 损失 J = - (1/N^2)*sum_{i,j} kernel, 这里暂不做归一化

//                 // 对 w 的贡献： (e_i - e_j)/(2σ²)*kernel * (v_i - v_j)
//                 double factor = (diff) / (2 * sigma * sigma) * kernel;
//                 for (int d = 0; d < k; d++) {
//                     grad_w[d] += factor * (X[i][d] - X[j][d]);
//                 }
//             }
//         }

//         // 平均归一化
//         loss /= (N * N);
//         for (int d = 0; d < k; d++) {
//             grad_w[d] /= (N * N);
//         }

//         // 输出当前迭代的损失值（负信息势越小越好）
//         if ((iter + 1) % 100 == 0)
//             std::cout << "Iteration " << iter+1 << ", Loss = " << loss << std::endl;

//         // 3. 更新 w (s 对信息势损失梯度为 0，这里不更新 s)
//         for (int d = 0; d < k; d++) {
//             w[d] -= learningRate * grad_w[d];
//         }

//         if(1.0 - loss < 1e-4) {
//             break;
//         }
//         // if(1.0 - loss < 0.05) {
//         //     learningRate = 0.0001;
//         // }
//     }
// }


}  // namespace SZ3
#endif  // SZ_ParamTuning_HPP
