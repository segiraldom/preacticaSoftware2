<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UserController; #
use App\Http\Controllers\AccountController; #

Route::post("/register", [UserController::class, 'register']); #
Route::post("/login", [UserController::class, 'login']); #
Route::put("/password/reset", [UserController::class, 'resetPassword']); #

Route::middleware('auth:sanctum')->group(function () {
    Route::post("/logout", [UserController::class, 'logout']); #
});

