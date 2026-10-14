# 1. Two Sum

## Metadata

- Created: 2026-10-13
- Next review: 2026-10-16

## My Attempt

```python
class Solution:
    def twoSum(self, nums, target):
        for i in range(len(nums)):
            for j in range(len(nums)):
                if nums[i] + nums[j] == target:
                    return [i, j]
        return []
```

## AI Review

## Verdict
The solution is **partially correct but not accepted**.

## Test Results
Passed:
- `[2, 7, 11, 15], target = 9` → `[0, 1]`
- `[-1, -2, -3, -4, -5], target = -8` → `[2, 4]`

Failed:
- `[3, 2, 4], target = 6`  
  Expected `[1, 2]`, got `[0, 0]`
- `[3, 3], target = 6`  
  Expected `[0, 1]`, got `[0, 0]`

## Current Approach
The code checks every pair of indices with two nested loops:

```python
for i in range(len(nums)):
    for j in range(len(nums)):
        if nums[i] + nums[j] == target:
            return [i, j]
```

This brute-force method can find a valid pair, but it also allows using the **same element twice** because `i` and `j` can be equal.

## Issues and Misconceptions
- **Same index is allowed by the code**: `i == j` can happen, so the solution may return `[0, 0]` when `nums[0] + nums[0] == target`.
- **Incorrect for the problem rules**: the problem says the same element may not be used twice.
- **Order requirement**: the problem asks for the smaller index first. Your code happens to return indices in increasing order only when `i < j`, but it does not explicitly enforce that.
- **Efficiency**: this is `O(n^2)`, which is much slower than necessary.

## Related Past Mistakes
I did not search your notebook for related cards.

## Improved Approach
A standard fix is to use a hash map:

- Scan the array once.
- For each number `x` at index `i`, compute `need = target - x`.
- If `need` was seen before, return its index and `i`.
- Otherwise store `x -> i`.

This avoids using the same element twice and runs in linear time.

Example:

```python
class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, x in enumerate(nums):
            need = target - x
            if need in seen:
                return [seen[need], i]
            seen[x] = i
```

## Complexity Analysis
- **Current solution:** `O(n^2)` time, `O(1)` extra space
- **Improved solution:** `O(n)` time, `O(n)` extra space

## Next-Time Reminder
When a problem says “the same element may not be used twice,” make sure your loops or logic exclude `i == j`.

## Reflection

- Why did I choose my original approach?
- What signal should remind me to use the better approach next time?
- Can I solve a similar problem without looking at the answer?
