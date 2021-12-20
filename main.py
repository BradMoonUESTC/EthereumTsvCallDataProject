import pandas as pd
# block_id	transaction_hash	index	depth	time
# failed	fail_reason	type	sender	recipient	child_call_count
# value	value_usd	transferred	input_hex	output_hex

#以多维数组的方式返回比较基准数据（类似一个窗口从上往下滑动并进行比对）
def getWindowWithSenderAndRecipient(txs,windowCount):
    list=[]
    txs=txs.reset_index(drop=True)#重置索引
    if windowCount==1:
        for j in range(len(txs)):
            list_child=[txs['type'][j],txs['sender'][j],txs['recipient'][j]]
            if list_child not in list:
                list.append(list_child)
    if windowCount>1:
        for i in range(len(txs)-windowCount+1):
            list_window = []
            for j in range(windowCount):
                list_grandchild=[txs['type'][i+j],txs['sender'][i+j],txs['recipient'][i+j]]
                list_window.append(list_grandchild)
            if list_window not in list:
                #检查list_window当中的list_grandchild是不是全部相同
                flag=1
                for i in range(len(list_window)):
                    if list_window[0]!=list_window[i]:
                        flag=0

                if flag==0:
                    list.append(list_window)
                #01234 5-2+1=4
    return list

#看看比较基准（窗口数据）在整个数据中出现了几次（连续出现）
#一旦出现第一个匹配，则+windowcount继续比对，否则+1比对，但是一旦出现不同，则+1比对，遇到之后再次+windowcount比对，最后计算总共匹配到的次数
#必须保证连续 n 次比对成功才可以+1匹配到的次数,n是一个阈值
def countWindowAppearsInData(txs,list_windowBase,n):
    txs=txs.reset_index(drop=True)#重置索引
    windowCount=len(list_windowBase)#滑动窗口的高度
    length=len(txs)#总长度
    count=0
    countForN=0
    listCountForNANdCount=[]
    listAll=[]
    i=0
    while i <= length-windowCount+1:
        if length-i>=windowCount:

            #从i到i+windowCount拿出txs中的数据
            list_windowCompare=[]
            for j in range(windowCount):
                list_grandchild=[txs['type'][i+j],txs['sender'][i+j],txs['recipient'][i+j]]
                list_windowCompare.append(list_grandchild)

            #用从txs拿出来的数据与基准进行比对，并记录出现次数
            if list_windowBase==list_windowCompare:
                #出现了一次匹配，将i移动到i+windowCount
                i+=windowCount
                countForN=countForN+1
            if list_windowBase!=list_windowCompare:
                # 没有出现匹配，但是之前的比较已经连续出现了大于等于n次了，则对n+1,并将countForN置0同时i+1
                if countForN>=n:
                    count=count+1
                    listCountForNANdCount.append(countForN)
                    listCountForNANdCount.append(count)
                    listAll.append(listCountForNANdCount)
                    listCountForNANdCount=[]
                countForN=0
                i=i+1
            if i>length-windowCount+1:
                if countForN>=n:
                    count=count+1
                    listCountForNANdCount.append(countForN)
                    listCountForNANdCount.append(count)
                    listAll.append(listCountForNANdCount)
                    listCountForNANdCount = []
                #do nothing
        else:
            break
    return listAll
if __name__ == '__main__':
    file_path=r'C:\Users\nerbonic\Desktop\new.tsv'
    threshold=3 #阈值 指滑动窗口连续匹配到的次数，大于这个阈值才会被认定为重入可能
    windowCount=3 #设置滑动窗口大小
    datas = pd.read_csv(file_path, sep='\t', header=0,index_col=None)
    wp = datas.drop_duplicates(['transaction_hash'])

    print('————————————————————————————————————————当前阈值：'+str(threshold)+'————————————————————————————————————————————')
    print('—————————————————————————————————————当前滑动窗口大小：' + str(windowCount) + '————————————————————————————————————————')
    for hash in wp['transaction_hash'].values:
        if len(hash)!=64:
            continue
        txs = datas[datas['transaction_hash'] == hash]
        #print(txs['block_id'])
        list_windowBase=getWindowWithSenderAndRecipient(txs,windowCount)
        for list in list_windowBase:

            # 检查list_window当中必须至少两个call（类似call+delegatecall+delegatecall不算重入）
            # 最后一个sender必须在前面出现过
            count = 0
            flag = 1
            for i in range(len(list)):
                if list[i][0] == 'call':
                    count = count + 1
            for i in range(len(list)-1):
                if list[len(list)-1][1] in list[i]:
                    flag = 0

            #第一个的sender必须和最后一个recipient一样
            #list[0][1] == list[len(list)-1][2]



            if(count>=2)&((list[0][1]) == (list[len(list)-1][2]))&(flag==0):
                listAll=countWindowAppearsInData(txs, list, threshold)
                if len(listAll)!=0:
                    print('———————当前交易哈希：0x' + hash + '————————')
                    print('———————————————————————————当前滑动窗口—————————————————————————————————')
                    print(list)
                    print('———————————————————————————窗口滑动结果：[连续次数，出现连续的次数]—————————————————————————————————')

                    print(listAll)
                    print('————————————————————————————————————————————————————————————————————————')

