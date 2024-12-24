; ModuleID = "main"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

@"true" = constant i1 1
@"false" = constant i1 0
define i32 @"fib"(i32 %".1")
{
fib_entry:
  %".3" = alloca i32
  store i32 %".1", i32* %".3"
  %".5" = load i32, i32* %".3"
  %".6" = icmp eq i32 %".5", 0
  br i1 %".6", label %"fib_entry.if", label %"fib_entry.endif"
fib_entry.if:
  ret i32 0
fib_entry.endif:
  %".9" = load i32, i32* %".3"
  %".10" = icmp eq i32 %".9", 1
  br i1 %".10", label %"fib_entry.endif.if", label %"fib_entry.endif.endif"
fib_entry.endif.if:
  ret i32 1
fib_entry.endif.endif:
  %".13" = load i32, i32* %".3"
  %".14" = sub i32 %".13", 1
  %".15" = call i32 @"fib"(i32 %".14")
  %".16" = load i32, i32* %".3"
  %".17" = sub i32 %".16", 2
  %".18" = call i32 @"fib"(i32 %".17")
  %".19" = add i32 %".15", %".18"
  ret i32 %".19"
}
