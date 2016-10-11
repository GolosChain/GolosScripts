require 'json'

accounts = JSON.parse(File.read('snapshot_balances.json'))

sharedrop = []
total_fund = 0.0
sharedrop_balance = 4512000.0 - accounts.size * 5.0
only_registration = 0

accounts.each do |account|
  total_fund += account['balance']
end

class Float
  def floor2(exp = 0)
   multiplier = 10 ** exp
   ((self * multiplier).floor).to_f/multiplier.to_f
  end
end

accounts.each do |account|
  balance = account['balance'].to_f
  if sharedrop_balance * balance / total_fund > 5.0
    sharedrop_amount = sharedrop_balance * balance / total_fund
    account_summary = {
      account: account['name'],
      amount: sharedrop_amount.floor2(1)
    }
    sharedrop << account_summary
  else
    only_registration += 1
  end
end

File.open("sharedrop_balances.json","w") do |f|
  f.write(JSON.pretty_generate(sharedrop))
end

puts "Needs to fund accounts: " + (accounts.size - only_registration).to_s
puts "Don't need to fund accounts: " + only_registration.to_s
puts "Done"
