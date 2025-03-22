cmake_minimum_required(VERSION 3.10)
project(FHDE)

add_executable(fhde fhde.cpp)

install(TARGETS fhde RUNTIME DESTINATION bin)