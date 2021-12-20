import pandas as pd
if __name__ == '__main__':
    list_all = []
    with open(r'C:\Users\nerbonic\Desktop\聚合了202004182020091720200713三天的数据.txt', 'r', encoding='utf-8') as f:
        list_child = []
        count=0
        line=f.readlines()[0]
        list_all=eval(line)

    # print(list_all)
    list_routerProblemSenderAndRecipient=[]


    notRouterCount=0
    list_notRouter=[]
    map_noRouterSender=dict()
    map_noRouterRecipient=dict()
    # [['0x0000000000051666bbfbb42925c3ee5d50cf6b10', '0x60594a405d53811d3bc4766596efd80fd545a270'],
    #  ['00000.00000', '00000.00000.00002.00000.00002.00000'],
    #  ['128acb08', '128acb08'],
    #  ['0x60594a405d53811d3bc4766596efd80fd545a270', '0x0000000000051666bbfbb42925c3ee5d50cf6b10'],
    #  '8017908c474dfacbec3c186e9aefea88ee1ea4062f89affd9b20efa8946f9ee9']
    list_excpet=[]
    list_hash=[]
    map_uniswapV2RouterUnknownAddress=dict()
    map_uniswapV3RouterUnknownAddress=dict()
    map_uniswapV3SwapFuntionAddress=dict()
    map_uniswapV2SwapFunctionAddress=dict()
    map_creamFinanceReentrancyAddress=dict()
    map_ERC223TokenFallbackFunctionAddress=dict()
    map_ERC777ReentrancyAddress=dict()
    map_except=dict()
    #region 筛选出相同txhash的
    list_filted_all=[]
    for list in list_all:
        txhash=list[4]
        if txhash not in list_hash:
            list_hash.append(txhash)
            list_filted_all.append(list)
    #endregion 筛选出相同txhash的
    uniswapV2RouterCount=0
    uniswapV3RouterCount=0
    uniswapV3SwapFunctionCount=0
    uniswapV2SwapFunctionCount=0
    creamFinanceReentrancyCount=0
    ERC223TokenFallbackFunctionCount=0
    ERC777ReentrancyAddressCount=0
    exceptCount=0
    print("总共的交易数：")
    print(len(list_filted_all))

    for list in list_filted_all:

        #region 取出数据
        list_senderAndRecipient=list[0]
        list_index=list[1]
        list_path=list[3]
        txhash=list[4]
        functionBytes=list[2]
        #endregion

        sender = list_senderAndRecipient[0]
        recipient=list_senderAndRecipient[1]
        if ('0x7a250d5630b4cf539739df2c5dacb4c659f2488d' == sender) | (
                '0x7a250d5630b4cf539739df2c5dacb4c659f2488d' == recipient):
            uniswapV2RouterCount+=1
            if sender!='0x7a250d5630b4cf539739df2c5dacb4c659f2488d':
                if sender not in map_uniswapV2RouterUnknownAddress:
                    map_uniswapV2RouterUnknownAddress[sender] = 0
                    map_uniswapV2RouterUnknownAddress[sender]+=1

                else:
                    map_uniswapV2RouterUnknownAddress[sender]+=1
            if recipient!='0x7a250d5630b4cf539739df2c5dacb4c659f2488d':
                if recipient not in map_uniswapV2RouterUnknownAddress:
                    map_uniswapV2RouterUnknownAddress[recipient] = 0
                    map_uniswapV2RouterUnknownAddress[recipient]+=1
                else:
                    map_uniswapV2RouterUnknownAddress[recipient]+=1
        elif ('0xe592427a0aece92de3edee1f18e0157c05861564' == sender) | (
                '0xe592427a0aece92de3edee1f18e0157c05861564' == recipient):
            uniswapV3RouterCount+=1
            if sender!='0xe592427a0aece92de3edee1f18e0157c05861564':
                if sender not in map_uniswapV3RouterUnknownAddress:
                    map_uniswapV3RouterUnknownAddress[sender] = 0
                    map_uniswapV3RouterUnknownAddress[sender]+=1

                else:
                    map_uniswapV3RouterUnknownAddress[sender]+=1
            if recipient!='0xe592427a0aece92de3edee1f18e0157c05861564':
                if recipient not in map_uniswapV3RouterUnknownAddress:
                    map_uniswapV3RouterUnknownAddress[recipient] = 0
                    map_uniswapV3RouterUnknownAddress[recipient]+=1

                else:
                    map_uniswapV3RouterUnknownAddress[recipient]+=1
        elif ('0xbd2250d713bf98b7e00c26e2907370ad30f0891a' == sender) | (
                '0xbd2250d713bf98b7e00c26e2907370ad30f0891a' == recipient):
            ERC777ReentrancyAddressCount+=1
            if sender!='0xbd2250d713bf98b7e00c26e2907370ad30f0891a':
                if sender not in map_ERC777ReentrancyAddress:
                    map_ERC777ReentrancyAddress[sender] = 0
                    map_ERC777ReentrancyAddress[sender]+=1

                else:
                    map_ERC777ReentrancyAddress[sender]+=1
            if recipient!='0xbd2250d713bf98b7e00c26e2907370ad30f0891a':
                if recipient not in map_ERC777ReentrancyAddress:
                    map_ERC777ReentrancyAddress[recipient] = 0
                    map_ERC777ReentrancyAddress[recipient]+=1

                else:
                    map_ERC777ReentrancyAddress[recipient]+=1
        elif functionBytes[0]=='128acb08':
            uniswapV3SwapFunctionCount+=1
            if sender not in map_uniswapV3SwapFuntionAddress:
                map_uniswapV3SwapFuntionAddress[sender] = 0
                map_uniswapV3SwapFuntionAddress[sender] += 1
            else:
                map_uniswapV3SwapFuntionAddress[sender] += 1
            if recipient not in map_uniswapV3SwapFuntionAddress:
                map_uniswapV3SwapFuntionAddress[recipient] = 0
                map_uniswapV3SwapFuntionAddress[recipient] += 1
            else:
                map_uniswapV3SwapFuntionAddress[recipient] += 1
        elif functionBytes[0]=='022c0d9f':
            uniswapV2SwapFunctionCount+=1
            if sender not in map_uniswapV2SwapFunctionAddress:
                map_uniswapV2SwapFunctionAddress[sender] = 0
                map_uniswapV2SwapFunctionAddress[sender] += 1
            else:
                map_uniswapV2SwapFunctionAddress[sender] += 1
            if recipient not in map_uniswapV2SwapFunctionAddress:
                map_uniswapV2SwapFunctionAddress[recipient] = 0
                map_uniswapV2SwapFunctionAddress[recipient] += 1
            else:
                map_uniswapV2SwapFunctionAddress[recipient] += 1
        elif ('0xcf919297690c6564d62f064969cc8ff5f5689ccc' == sender) | (
                '0xcf919297690c6564d62f064969cc8ff5f5689ccc' == recipient):
            creamFinanceReentrancyCount+=1
            if sender!='0xcf919297690c6564d62f064969cc8ff5f5689ccc':
                if sender not in map_creamFinanceReentrancyAddress:
                    map_creamFinanceReentrancyAddress[sender] = 0
                    map_creamFinanceReentrancyAddress[sender]+=1

                else:
                    map_creamFinanceReentrancyAddress[sender]+=1
            if recipient!='0xcf919297690c6564d62f064969cc8ff5f5689ccc':
                if recipient not in map_creamFinanceReentrancyAddress:
                    map_creamFinanceReentrancyAddress[recipient] = 0
                    map_creamFinanceReentrancyAddress[recipient]+=1

                else:
                    map_creamFinanceReentrancyAddress[recipient]+=1
        elif functionBytes[0] == 'c0ee0b8a':
            ERC223TokenFallbackFunctionCount += 1
            if sender not in map_ERC223TokenFallbackFunctionAddress:
                map_ERC223TokenFallbackFunctionAddress[sender] = 0
                map_ERC223TokenFallbackFunctionAddress[sender] += 1
            else:
                map_ERC223TokenFallbackFunctionAddress[sender] += 1
            if recipient not in map_ERC223TokenFallbackFunctionAddress:
                map_ERC223TokenFallbackFunctionAddress[recipient] = 0
                map_ERC223TokenFallbackFunctionAddress[recipient] += 1
            else:
                map_ERC223TokenFallbackFunctionAddress[recipient] += 1
        else:
            exceptCount+=1
            if sender not in map_except:
                map_except[sender] = 0
                map_except[sender]+=1
            else:
                map_except[sender]+=1
            if recipient not in map_except:
                map_except[recipient] = 0
                map_except[recipient] += 1
            else:
                map_except[recipient]+=1
            list_excpet.append(list)

    print("————————数据1——与uniswapV2Router相关的数据————————")
    print("交易总数:")
    print(str(uniswapV2RouterCount))
    print("奇怪的地址：")
    print(map_uniswapV2RouterUnknownAddress)
    print("地址总数：")
    print(str(len(map_uniswapV2RouterUnknownAddress)))

    print("————————数据2——与uniswapV3Router相关的数据————————")
    print("交易总数:")
    print(str(uniswapV3RouterCount))
    print("奇怪的地址，以及各出现了多少次")
    print(map_uniswapV3RouterUnknownAddress)
    print("地址总数：")
    print(str(len(map_uniswapV3RouterUnknownAddress)))
    print("————————数据3——与uniswapV3Pool中调用swap与swapcallback相关的数据————————")
    print("交易总数:")
    print(str(uniswapV3SwapFunctionCount))
    print("奇怪的地址，以及各出现了多少次")
    print(map_uniswapV3SwapFuntionAddress)
    print("地址总数：")
    print(str(len(map_uniswapV3SwapFuntionAddress)))
    print("————————数据4——与uniswapV2Pool中调用swap与swapcallback相关的数据————————")
    print("交易总数:")
    print(str(uniswapV2SwapFunctionCount))
    print("奇怪的地址，以及各出现了多少次")
    print(map_uniswapV2SwapFunctionAddress)
    print("地址总数：")
    print(str(len(map_uniswapV2SwapFunctionAddress)))
    print("————————数据5——与cream Finance重入相关的数据————————")
    print("交易总数:")
    print(str(creamFinanceReentrancyCount))
    print("涉及的地址，以及各出现了多少次")
    print(map_creamFinanceReentrancyAddress)
    print("地址总数：")
    print(str(len(map_creamFinanceReentrancyAddress)))
    print("————————数据6——与ERC777重入相关的数据————————")
    print("交易总数:")
    print(str(ERC777ReentrancyAddressCount))
    print("奇怪的地址，以及各出现了多少次")
    print(map_ERC777ReentrancyAddress)
    print("地址总数：")
    print(str(len(map_ERC777ReentrancyAddress)))
    print("————————数据7——因ERC223标准造成的疑似重入————————")
    #region ERC223的解释
    '''开发人员Dexaran详细描述了ERC-223标准适用的两种场景：
    在ERC20通证标准中执行交易有两种方式:
    
    1.transfer方法。
    
    2.approve + transferFrom 机制。
    
    Token余额只是通证合约中的一个变量。
    
    Token的交易在合约中的表现是变量的变化：转出账户的余额将减少，接收账户的余额将增多。
    
    交易发生时， transfer方法不会通知接收账户，接受账户也将无法识别传入交易！下面是我写的一个例子，来展示导致交易未处理和资金损失的过程 。
    
    如果接收账户接受到的是合约，用户必须使用approve +transferFrom 机制来转移通证；如果接收账户是外部帐户地址，用户必须通过 transfer方法转移Token；如果选择了错误的方法，token将被卡在合约中(合约将不会识别交易)，那么，我们将无法提取这些被卡住的token。
    
    Dexaran提出的ERC-223标准就解决了这一问题，而且，它与ERC-20标准非常相似。当token转移到智能合约时，该合约的一个特殊方法tokenFallback将允许接收合约、拒绝通证或触发进一步的操作。在大多数情况下，tokenFallback方法可以用来代替approve方法。
    '''
    #endregion
    print("交易总数:")
    print(str(ERC223TokenFallbackFunctionCount))
    print("奇怪的地址，以及各出现了多少次")
    print(map_ERC223TokenFallbackFunctionAddress)
    print("地址总数：")
    print(str(len(map_ERC223TokenFallbackFunctionAddress)))

    print("————————数据8——其他数据————————")
    print("交易总数:")
    print(str(exceptCount))
    print(list_excpet)
    print("都设计了哪些地址，出现的次数")
    print(map_except)






