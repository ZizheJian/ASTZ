#ifndef FHDE_TIMER_HPP
#define FHDE_TIMER_HPP

#include <chrono>
#include <iostream>
#include <string>

namespace FHDE{
class Timer{
    public:
    Timer()=default;

    Timer(bool initstart)
    {
        if (initstart)
            start();
    }

    void start()
    {
        begin=std::chrono::steady_clock::now();
    }

    double stop()
    {
        end=std::chrono::steady_clock::now();
        return std::chrono::duration<double>(end-begin).count();
    }

    private:
    std::chrono::time_point<std::chrono::steady_clock> begin, end;
};
}

#endif
