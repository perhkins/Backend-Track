def two_sum_unsorted(nums:list[int], target:int):
    """
    Find two numbers in an unsorted list that add up to a specific target.

    Args:
        nums (list): A list of integers.
        target (int): The target sum.

    Returns:
        tuple: A tuple containing the indices of the two numbers that add up to the target, or None if no such pair exists.

    The function uses a hash map to store the indices of the numbers as it iterates through the list, allowing for efficient lookups of the complement needed to reach the target.

    Algorithmic Complexity:
    - Time Complexity: O(n), where n is the number of elements in the list.
    - Space Complexity: O(n), as the function uses a hash map to store the indices of the numbers.
    """
    num_dict = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_dict:
            return (num_dict[complement], i)
        num_dict[num] = i
    return None

def main():
    #Test Cases
    print(two_sum_unsorted([2, 7, 11, 15], 9) == (0, 1))
    print(two_sum_unsorted([3, 2, 4], 6) == (1, 2))
    print(two_sum_unsorted([3, 3], 6) == (0, 1))
    print(two_sum_unsorted([1, 5, 8, 3, 2], 11) == (2, 3))

if __name__ == "__main__":
    main()