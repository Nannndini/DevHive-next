import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;
  
  // Define paths that don't require authentication
  const isPublicPath = request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/register';
  
  if (!token && !isPublicPath) {
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