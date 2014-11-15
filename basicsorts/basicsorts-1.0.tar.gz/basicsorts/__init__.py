from heapq import merge

def bubbleSort(arr0):
    arr=arr0[:]
    changed = True
    while changed:
        changed = False
        for i in xrange(len(arr) - 1):
            if arr[i] > arr[i+1]:
                arr[i], arr[i+1] = arr[i+1], arr[i]
                changed = True
    return arr

def heapSort(arr0):
  arr=arr0[:]
  # in pseudo-code, heapify only called once, so inline it here
  for start in range((len(arr)-2)/2, -1, -1):
    siftdown(arr, start, len(arr)-1)
 
  for end in range(len(arr)-1, 0, -1):
    arr[end], arr[0] = arr[0], arr[end]
    siftdown(arr, 0, end - 1)
  return arr

 
def siftdown(arr, start, end):
  root = start
  while True:
    child = root * 2 + 1
    if child > end: break
    if child + 1 <= end and arr[child] < arr[child + 1]:
      child += 1
    if arr[root] < arr[child]:
      arr[root], arr[child] = arr[child], arr[root]
      root = child
    else:
      break

def insertionSort(arr0):
    arr=arr0[:]
    for i in xrange(1, len(arr)):
        j = i-1 
        key = arr[i]
        while (arr[j] > key) and (j >= 0):
           arr[j+1] = arr[j]
           j -= 1
        arr[j+1] = key
    return arr
 
def mergeSort(arr):
    if len(arr) <= 1:
        return arr
 
    middle = len(arr) / 2
    left = arr[:middle]
    right = arr[middle:]
 
    left = mergeSort(left)
    right = mergeSort(right)
    return list(merge(left, right))

def quickSort(arr):
    less = []
    pivotList = []
    more = []
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        for i in arr:
            if i < pivot:
                less.append(i)
            elif i > pivot:
                more.append(i)
            else:
                pivotList.append(i)
        less = quickSort(less)
        more = quickSort(more)
        return less + pivotList + more

def selectionSort(arr0):
    arr=arr0[:]
    for i in range(0,len(arr)-1):
        mn = min(range(i,len(arr)), key=arr.__getitem__)
        arr[i],arr[mn] = arr[mn],arr[i]
    return arr

