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



}  // namespace SZ3
#endif  // SZ_ParamTuning_HPP
