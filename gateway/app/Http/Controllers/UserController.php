<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Validation\ValidationException;
Use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    public function register(Request $request)
    {
        $validated = $request->validate([
            'name' => ['required', 'string', 'max:255'],
            'document' => ['required', 'string', 'max:255', 'unique:users,document'],
            'question' => ['required', 'in:Mascota,Color favorito,Comida favorita'],
            'answer' => ['required', 'string', 'max:255'],
            'email' => ['required', 'string', 'email', 'max:255', 'unique:users,email'],
            'password' => ['required', 'string', 'min:8'],
        ]);

        $user = User::create($validated);

        return response()->json($user, 201);
    }

    public function login(Request $request)
    {
        $request->validate([
            'email' => ['required', 'string', 'email'],
            'password' => ['required', 'string'],
        ]);

        $user = User::where('email', $request->email)->first();
        if(!$user){
            return response()->json([
                "response"=>"Este correo no existe"
            ], 404);
        }
        if(!Hash::check($request->password, $user->password)){
            return response()->json([
                "response"=>"Credenciales incorrectas"
            ], 401);
        }
        $token = $user->createToken('auth_token')->plainTextToken;
        return response()->json([
            "token"=>$token,
            "user"=>$user,
            "response"=>"Bienvenido"
        ],200);
    }

    public function logout(Request $request)
    {
        $request->user()->currentAccessToken()->delete();

        return response()->json([
            'message' => 'Sesión cerrada correctamente.',
        ]);
    }

    public function resetPassword(Request $request)
    {
        $validated = $request->validate([
            'email' => ['required', 'string', 'email'],
            'question' => ['required', 'in:Mascota,Color favorito,Comida favorita'],
            'answer' => ['required', 'string', 'max:255'],
            'password' => ['required', 'string', 'min:8', 'confirmed'],
        ], [
            'password.confirmed' => 'La confirmación de la contraseña no coincide.',
        ]);

        $user = User::where('email', $validated['email'])->first();

        if (! $user) {
            throw ValidationException::withMessages([
                'email' => ['No existe ninguna cuenta registrada con ese correo.'],
            ]);
        }

        $answerMatches = hash_equals(
            mb_strtolower(trim($user->answer)),
            mb_strtolower(trim($validated['answer']))
        );

        if ($user->question !== $validated['question'] || ! $answerMatches) {
            throw ValidationException::withMessages([
                'answer' => ['La pregunta o la respuesta de seguridad no son correctas.'],
            ]);
        }

        $user->password = $validated['password'];
        $user->save();

        return response()->json([
            'message' => 'Contraseña actualizada correctamente.',
        ]);
    }

}
