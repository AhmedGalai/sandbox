import torch
import time

def test_gpu():
    print("PyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if not torch.cuda.is_available():
        return

    device = torch.device("cuda")

    # Small tensor for lightweight test
    a = torch.randn(1024, 1024, device=device)
    b = torch.randn(1024, 1024, device=device)

    # Warm-up (important for accurate timing)
    for _ in range(3):
        x = torch.matmul(a, b)
        torch.cuda.synchronize()

    # Benchmark
    start = time.time()
    x = torch.matmul(a, b)
    torch.cuda.synchronize()  # wait for GPU to finish
    end = time.time()

    print(f"Matrix multiply time: {end - start:.6f} seconds")
    print("Result sample:", x[0, 0].item())


if __name__ == "__main__":
    test_gpu()
