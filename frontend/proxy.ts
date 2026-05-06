import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;
  
  // Debug logs
  console.log("Middleware executing for path:", request.nextUrl.pathname);
  console.log("Middleware token found:", token);
  
  // Define paths that don't require authentication
  const isPublicPath = request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/register';
  
  if (!token && !isPublicPath) {
    console.log("Redirecting unauthenticated user to /login");
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  if (token && isPublicPath) {
    return NextResponse.redirect(new URL('/', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ]
}