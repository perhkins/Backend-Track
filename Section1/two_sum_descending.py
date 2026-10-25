def two_sum_descending(nums, target):
    """
    Find two numbers in a descending sorted list that add up to the target.

    Args:
        nums (List[int]): A list of integers sorted in descending order.
        target (int): The target sum.

    Returns:
        tuple: A tuple containing the indices of the two numbers that add up to the target, or None if no such pair exists.

    The function uses a two-pointer approach to find the pair of numbers that add up to the target.

    Algorithmic Complexity:
    - Time Complexity: O(n), where n is the number of elements in the list.
    - Space Complexity: O(1), as the function only uses a constant amount of extra space.
    """
    left = 0
    right = len(nums) - 1

    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            return (left, right)
        elif current_sum > target:
            left += 1
        else:
            right -= 1

    return None

def main():
    # Test Cases
    print(two_sum_descending([15, 11, 7, 2], 9) == (2, 3))
    print(two_sum_descending([10, 8, 5, 3, 2, 1], 10) == (1, 4))
    print(two_sum_descending([20, 14, 11, 8, 4, 1], 15) in [(1, 5), (2, 4)])
    print(two_sum_descending([9, 7, 4, 3, 1], 10) in [(0, 4), (1, 3)])

if __name__ == "__main__":
    main()