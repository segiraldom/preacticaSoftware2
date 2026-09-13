<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class AccountController extends Controller
{
    public function example(Request $request){
        $response = Http::post('http://localhost:5000/example',[
            "dato" => "Mensaje enviado desde Laravel" 
        ]);
        return response()->jason($response->json(), 200);
    }
}
