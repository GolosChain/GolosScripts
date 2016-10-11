require 'json'

snapshot = JSON.parse(File.read('snapshot5392323.json'))

total_vesting_fund_steem = snapshot['summary']['total_vesting_fund_steem'].split(' ')[0].tr(',','').to_f
total_vesting_shares = snapshot['summary']['total_vesting_shares'].split(' ')[0].tr(',','').to_f
price = (total_vesting_fund_steem / total_vesting_shares).round(8)

puts "Total vesting fund Steem: " + total_vesting_fund_steem.to_s
puts "Total vesting shares: " + total_vesting_shares.to_s
puts "Price: " + price.to_s

sharedrop = []
total_balance = 0

accounts = snapshot['accounts'].each do |account|
  balance = account['balances']['assets']
  steem = balance[0].split(' ')[0].tr(',','').to_f
  steem_power = balance[2].split(' ')[0].tr(',','').to_f * price
  summary_balance = (steem + steem_power).round(4)
  total_balance += summary_balance
  account_summary = {
    name: account['name'],
    balance: summary_balance
  }
  sharedrop << account_summary
end

File.open("snapshot_balances.json","w") do |f|
  f.write(JSON.pretty_generate(sharedrop))
end

puts "Number of accounts: " + accounts.size.to_s
puts "Total balance to drop: " + total_balance.to_s
puts "Done"
