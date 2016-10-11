require 'json'

snapshot = JSON.parse(File.read('steem_snapshot_1475150400.json'))

total_vesting_fund_steem = snapshot['summary']['total_vesting_fund_steem'].split(' ')[0].tr(',','').to_f
total_vesting_shares = snapshot['summary']['total_vesting_shares'].split(' ')[0].tr(',','').to_f
price = (total_vesting_fund_steem / total_vesting_shares).round(8)

puts "Total vesting fund Steem: " + total_vesting_fund_steem.to_s
puts "Total vesting shares: " + total_vesting_shares.to_s
puts "Price: " + price.to_s

sharedrop_accounts = []
dust_accounts = 0
total_balance = 0
threshold = 7.0

public
def changeprefix!
   self["keys"].each do |type|
     type.each do |t|
       if t['key_auths']
         t['key_auths'].each do |pair|
           pair[0][0..2] = "GLS"
         end
       elsif t[0] != 'o' && t[0] != 'a' && t[0] != 'p' && t[0] != 'm'
         t[0..2] = "GLS"
       end
     end
   end
   self
end

accounts = snapshot['accounts'].each do |account|
  balance = account['balances']['assets']
  steem = balance[0].split(' ')[0].tr(',','').to_f
  steem_power = balance[2].split(' ')[0].tr(',','').to_f * price
  summary_balance = (steem + steem_power).round(3)
  if ( steem_power > threshold && account['curation_rewards'].to_i > 0 ) || steem_power > 100.0
    total_balance += summary_balance
    account.changeprefix!
    sharedrop_accounts << account
  else
     dust_accounts+=1
  end
end

snapshot['accounts'] = sharedrop_accounts

File.open("snapshot5392323.json","w") do |f|
  f.write(JSON.pretty_generate(snapshot))
end

puts "Number of accounts: " + accounts.size.to_s
puts "Number of dust accounts accounts " + dust_accounts.to_s
puts "Number of positive accounts " + (accounts.size-dust_accounts).to_s
puts "Total balance to drop: " + total_balance.to_s
puts "Done"
