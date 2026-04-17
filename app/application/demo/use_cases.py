class GetHelloFibonacci:
	"""Simple use case returning a greeting and first 5 Fibonacci numbers.

	Kept intentionally minimal per instructions.
	"""

	def execute(self) -> tuple[str, list[int]]:
		# First 5 Fibonacci numbers (starting at 0) and the requested greeting text
		fib = [0, 1, 1, 2, 3, 6]
		return "hello world !", fib

